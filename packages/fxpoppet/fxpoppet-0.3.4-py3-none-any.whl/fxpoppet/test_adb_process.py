# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# pylint: disable=protected-access
from pathlib import Path, PurePosixPath
from shutil import rmtree

from ffpuppet.exceptions import BrowserTerminatedError
from pytest import mark, raises

from .adb_process import ADBLaunchError, ADBProcess, Reason
from .adb_session import ADBResult, ADBSession, ADBSessionError


def test_adb_process_basic(mocker):
    """test ADBProcess() basic features"""
    test_pkg = "org.test.preinstalled"
    fake_session = mocker.Mock(spec_set=ADBSession)
    with ADBProcess(test_pkg, fake_session) as proc:
        assert isinstance(proc._session, ADBSession)
        assert proc._package == test_pkg
        assert proc.logs is None
        assert proc.profile is None
        assert proc.reason == Reason.CLOSED
        assert proc.launches == 0
        assert not proc.is_running()
        assert not proc.is_healthy()
        assert proc.wait(timeout=0)
        assert proc._pid is None
        proc.close()
        assert not proc.logs


def test_adb_process_close(mocker):
    """test ADBProcess.close()"""
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.listdir.return_value = [PurePosixPath("fake.dmp")]
    fake_session.collect_logs.return_value = "log output..."
    fake_session.open_files.return_value = ()
    with ADBProcess("org.test.app", fake_session) as proc:
        # pretend we launched
        proc.reason = None
        proc.profile = PurePosixPath("on_device_profile")
        proc.close()
        assert proc.reason == Reason.ALERT
        assert proc.profile is None
        assert proc.logs is not None


def test_adb_process_close_device_error(mocker):
    """test ADBProcess.close() handle ADBSessionError"""
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.listdir.side_effect = ADBSessionError()
    with ADBProcess("org.test.app", fake_session) as proc:
        # pretend we launched
        proc.reason = None
        proc.profile = PurePosixPath("on_device_profile")
        proc.close()
        assert proc.reason == Reason.CLOSED
        assert proc.profile is None
        assert proc.logs is None


def test_adb_process_missing_package(mocker):
    """test creating device with unknown package"""
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.is_installed.return_value = False
    with raises(ADBSessionError, match="Package 'org.test.unknown' is not installed"):
        ADBProcess("org.test.unknown", fake_session)


def test_adb_process_unsupported_app(mocker):
    """test ADBProcess.launch() unsupported app"""
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.collect_logs.return_value = ""
    with (
        ADBProcess("org.some.app", fake_session) as proc,
        raises(ADBLaunchError, match="Unsupported package 'org.some.app'"),
    ):
        proc.launch("fake.url")


def test_adb_process_failed_bootstrap(mocker):
    """test ADBProcess.launch() failed bootstrap setup"""
    mocker.patch("fxpoppet.adb_process.Bootstrapper", autospec=True)
    mocker.patch("fxpoppet.adb_process.sleep", autospec=True)
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.collect_logs.return_value = ""
    fake_session.listdir.return_value = ()
    fake_session.get_pid.return_value = None
    fake_session.reverse.return_value = False
    with (
        ADBProcess("org.mozilla.fenix", fake_session) as proc,
        raises(ADBLaunchError, match="Could not reverse port"),
    ):
        proc.launch("fake.url")


def test_adb_process_package_already_running(mocker):
    """test ADBProcess.launch() package is running (bad state)"""
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.call.return_value = (1, "")
    fake_session.collect_logs.return_value = ""
    fake_session.listdir.return_value = ()
    fake_session.process_exists.return_value = False
    with ADBProcess("org.mozilla.fenix", fake_session) as proc:
        with raises(ADBLaunchError, match="'org.mozilla.fenix' is already running"):
            proc.launch("fake.url")
        assert not proc.is_running()
        proc.cleanup()
        assert proc.logs is None


# TODO: check config yaml output
# def test_adb_process_06(mocker, tmp_path):
#    """test ADBProcess.launch() check *-geckoview-config.yaml"""


@mark.parametrize(
    "env",
    [
        # no env
        None,
        # with environment variables
        {"test1": "1", "test2": "2"},
    ],
)
def test_adb_process_launch(mocker, env):
    """test ADBProcess.launch(), ADBProcess.is_running() and ADBProcess.is_healthy()"""
    mocker.patch("fxpoppet.adb_process.sleep", autospec=True)
    mocker.patch("fxpoppet.adb_process.time", side_effect=range(100))
    fake_bs = mocker.patch("fxpoppet.adb_process.Bootstrapper", autospec=True).create
    fake_bs.return_value.location = "http://localhost"
    fake_bs.return_value.port.return_value = 1234
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.shell.return_value = ADBResult(0, "Status: ok")
    fake_session.collect_logs.return_value = ""
    fake_session.get_pid.side_effect = (None, 1337)
    fake_session.listdir.return_value = ()
    # fake_session.process_exists.return_value = False
    with ADBProcess("org.mozilla.geckoview_example", fake_session) as proc:
        assert not proc.is_running()
        assert not proc.is_healthy()
        assert proc.launches == 0
        assert proc.launch("fake.url", env_mod=env, prefs_js=None)
        assert proc.is_running()
        assert proc.is_healthy()
        assert not proc.wait(timeout=3)
        assert proc.launches == 1
        assert proc.reason is None
        proc.close()
        assert proc._pid is None
        assert proc.logs
    assert fake_bs.return_value.wait.call_count == 1
    assert fake_bs.return_value.close.call_count == 1


def test_adb_process_launch_process_launch_failure(mocker):
    """test ADBProcess.launch() process launch failure"""
    mocker.patch("fxpoppet.adb_process.sleep", autospec=True)
    mocker.patch("fxpoppet.adb_process.time", side_effect=range(100))
    fake_bs = mocker.patch("fxpoppet.adb_process.Bootstrapper", autospec=True).create
    fake_bs.return_value.location = "http://localhost"
    fake_bs.return_value.port.return_value = 1234
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.shell.side_effect = (
        ADBResult(0, ""),
        ADBResult(1, ""),
        ADBResult(0, ""),
        ADBResult(0, ""),
        ADBResult(0, ""),
    )
    fake_session.collect_logs.return_value = ""
    fake_session.get_pid.return_value = None
    fake_session.listdir.return_value = ()
    with (
        ADBProcess("org.mozilla.geckoview_example", fake_session) as proc,
        raises(ADBLaunchError, match=r"Could not launch"),
    ):
        proc.launch("fake.url")
    assert fake_bs.return_value.wait.call_count == 0
    assert fake_bs.return_value.close.call_count == 1


def test_adb_process_launch_failure_during_boot(mocker):
    """test ADBProcess.launch() failure during boot"""
    mocker.patch("fxpoppet.adb_process.sleep", autospec=True)
    mocker.patch("fxpoppet.adb_process.time", side_effect=range(100))
    fake_bs = mocker.patch("fxpoppet.adb_process.Bootstrapper", autospec=True).create
    fake_bs.return_value.location = "http://localhost"
    fake_bs.return_value.port.return_value = 1234
    fake_bs.return_value.wait.side_effect = BrowserTerminatedError("launch failure")
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.shell.return_value = ADBResult(0, "Status: ok")
    fake_session.collect_logs.return_value = ""
    fake_session.get_pid.side_effect = (None, 1234)
    fake_session.listdir.return_value = ()
    with (
        ADBProcess("org.mozilla.geckoview_example", fake_session) as proc,
        raises(ADBLaunchError, match="launch failure"),
    ):
        proc.launch("fake.url")
    assert fake_bs.return_value.close.call_count == 1


def test_adb_process_launch_upload_prefs_failure(mocker):
    """test ADBProcess.launch() upload prefs failure"""
    mocker.patch("fxpoppet.adb_process.sleep", autospec=True)
    mocker.patch("fxpoppet.adb_process.time", side_effect=range(100))
    fake_bs = mocker.patch("fxpoppet.adb_process.Bootstrapper", autospec=True).create
    fake_bs.return_value.location = "http://localhost"
    fake_bs.return_value.port.return_value = 1234
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.shell.return_value = ADBResult(0, "")
    fake_session.push.return_value = False
    fake_session.collect_logs.return_value = ""
    fake_session.get_pid.return_value = None
    fake_session.listdir.return_value = ()
    with (
        ADBProcess("org.mozilla.geckoview_example", fake_session) as proc,
        raises(ADBLaunchError, match=r"Could not upload '.+-geckoview-config\.yaml'"),
    ):
        proc.launch("fake.url")
    assert fake_bs.return_value.wait.call_count == 0
    assert fake_bs.return_value.close.call_count == 1


def test_adb_process_wait_on_files(mocker):
    """test ADBProcess.wait_on_files()"""
    fake_bs = mocker.patch("fxpoppet.adb_process.Bootstrapper", autospec=True).create
    fake_bs.return_value.location = "http://localhost"
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.shell.return_value = ADBResult(0, "Status: ok")
    fake_session.collect_logs.return_value = ""
    fake_session.get_pid.side_effect = (None, 1337)
    fake_session.open_files.return_value = ((1, "some_file"),)
    fake_session.listdir.return_value = ()
    fake_session.realpath.side_effect = str.strip
    with ADBProcess("org.mozilla.geckoview_example", fake_session) as proc:
        proc.wait_on_files(["not_running"])
        assert proc.launch("fake.url")
        assert proc.wait_on_files([])
        mocker.patch("fxpoppet.adb_process.sleep", autospec=True)
        mocker.patch("fxpoppet.adb_process.time", side_effect=(1, 1, 2))
        fake_session.open_files.return_value = (
            (1, "some_file"),
            (1, "/existing/file.txt"),
        )
        assert not proc.wait_on_files(
            ["/existing/file.txt"], poll_rate=0.1, timeout=0.3
        )
        proc.close()


def test_adb_process_find_crashreports(mocker):
    """test ADBProcess.find_crashreports()"""
    mocker.patch("fxpoppet.adb_process.Bootstrapper", autospec=True)
    fake_session = mocker.Mock(spec_set=ADBSession)
    with ADBProcess("org.some.app", fake_session) as proc:
        proc.profile = PurePosixPath("profile_path")
        # no log or minidump files
        fake_session.listdir.return_value = []
        assert not any(proc.find_crashreports())
        # contains minidump file
        fake_session.listdir.side_effect = (
            [PurePosixPath("somefile.txt"), PurePosixPath("test.dmp")],
        )
        assert any(x.name == "test.dmp" for x in proc.find_crashreports())
        # contains missing path
        fake_session.listdir.side_effect = (FileNotFoundError("test"),)
        assert not any(proc.find_crashreports())


def test_adb_process_save_logs(mocker, tmp_path):
    """test ADBProcess.save_logs()"""
    mocker.patch("fxpoppet.adb_process.Bootstrapper", autospec=True)
    fake_session = mocker.Mock(spec_set=ADBSession)
    log_path = tmp_path / "src"
    log_path.mkdir()
    (log_path / "nested").mkdir()
    fake_log = log_path / "fake.txt"
    fake_log.touch()
    dmp_path = tmp_path / "dst"
    with ADBProcess("org.some.app", fake_session) as proc:
        # without proc.logs set
        proc.save_logs(dmp_path)
        # with proc.logs set
        proc.logs = log_path
        proc.save_logs(dmp_path)
    assert any(dmp_path.glob("fake.txt"))


def test_adb_process_process_logs(mocker, tmp_path):
    """test ADBProcess._process_logs()"""
    mocker.patch("fxpoppet.adb_process.Bootstrapper", autospec=True)
    mocker.patch("fxpoppet.adb_process.getenv", autospec=True, return_value="1")
    log_tmp = tmp_path / "log_tmp"
    mocker.patch(
        "fxpoppet.adb_process.mkdtemp",
        autospec=True,
        return_value=str(log_tmp),
    )

    def _fake_pull(src, _dst):
        (log_tmp / "unprocessed" / src.name).touch()

    fake_mdp = mocker.patch("fxpoppet.adb_process.MinidumpParser", autospec=True)
    fake_mdp.dmp_files.return_value = [log_tmp / "log.dmp"]
    fake_mdp.return_value.__enter__.return_value.create_log.return_value = (
        log_tmp / "unprocessed" / "log.dmp"
    )
    fake_session = mocker.Mock(spec_set=ADBSession)
    fake_session.collect_logs.return_value = "fake logcat data"
    fake_session.pull.side_effect = _fake_pull
    profile = tmp_path / "profile"
    profile.mkdir()
    with ADBProcess("org.some.app", fake_session) as proc:
        proc.profile = profile
        log_tmp.mkdir()
        # no extra logs
        proc._process_logs([])
        assert proc.logs is not None
        assert (proc.logs / "log_logcat.txt").is_file()
        # reset log dir
        rmtree(proc.logs)
        proc.logs = None
        log_tmp.mkdir()
        assert fake_mdp.call_count == 0
        assert fake_session.pull.call_count == 0
        # other logs available
        proc._process_logs([Path("log.dmp"), Path("asan_log.txt")])
        assert proc.logs.is_dir()
        assert (proc.logs / "log_logcat.txt").is_file()
        # dmp is copied but name is incorrect because if the need to patch
        assert (proc.logs / "log.dmp").is_file()
        assert fake_mdp.call_count == 1
        assert fake_session.pull.call_count == 2
        assert fake_mdp.return_value.__enter__.return_value.create_log.call_count == 1


def test_adb_process_split_logcat(tmp_path):
    """test ADBProcess._split_logcat()"""
    log_path = tmp_path / "logs"
    log_path.mkdir()
    # missing log_logcat.txt
    ADBProcess._split_logcat(log_path, "fake.package")
    assert not any(log_path.iterdir())
    # with log_logcat.txt
    (tmp_path / "logs" / "log_logcat.txt").write_text(
        "07-27 12:10:15.414  80  80 W art     :"
        " Unexpected CPU variant for X86 using defaults: x86\n"
        "07-27 12:10:15.430  90  90 I GeckoApplication:"
        " zerdatime 3349725 - application start\n"
        "07-27 12:10:15.442  90  44 I GeckoThread: preparing to run Gecko\n"
        "07-27 12:10:15.442  90  44 E GeckoLibLoad: Load sqlite start\n"
        "07-27 12:10:15.496  81  81 I GRALLOC-DRM: foo\n"
        "07-27 12:10:15.505  90  43 I GeckoDump: test, line1\n"
        "07-27 12:10:15.505  90  43 E GeckoApp: test, line2\n"
        "07-27 12:10:15.520  82  49 I EGL-DRI2: found extension DRI_Core version 1\n"
        "07-27 12:10:15.521  82  49 I OpenGLRenderer: Initialized EGL, version 1.4\n"
        "07-27 12:10:15.528  90  44 E GeckoLibLoad: Load sqlite done\n"
        "07-27 12:10:15.529  80  80 W art     : Suspending all threads took: 8.966ms\n"
        "07-27 12:10:15.533  90  44 E GeckoLibLoad: Load nss done\n"
        "07-27 12:39:27.188  39  39 W Fake  : asdf\n"
        "07-27 12:39:27.239  17  14 I InputReader:"
        " Reconfiguring input devices.  changes=0x00000010\n"
        "07-27 12:39:27.440  78  78 E android.os.Debug:"
        " failed to load memtrack module: 90\n"
        "07-27 12:39:27.441  78  78 I Radio-JNI: register_android_hardware_Radio DONE\n"
        "07-27 12:39:27.442 18461 18481 F MOZ_CRASH: Hit MOZ_CRASH(test) at gpp.rs:17\n"
        "07-27 12:39:27.443  90  90 I eckoThrea: potentially missed\n"
    )
    ADBProcess._split_logcat(log_path, "fake.package")
    assert any(log_path.iterdir())
    assert (tmp_path / "logs" / "log_stdout.txt").read_text().rstrip() == "test, line1"
    stderr_lines = (tmp_path / "logs" / "log_stderr.txt").read_text().splitlines()
    assert "test, line2" in stderr_lines
    assert "test, line1" not in stderr_lines
    assert len(stderr_lines) == 8


@mark.parametrize(
    "input_data, result",
    [
        ("", {}),
        ("//comment\n", {}),
        ('junk\n#user_pref("a.b", 0);\n', {}),
        ('user_pref("a.b.c", false);\n', {"a.b.c": False}),
        ("user_pref('a.b.c', 0);", {"a.b.c": 0}),
        ("user_pref(\"a.b.c\", 'test');", {"a.b.c": "test"}),
        ('user_pref("a.b.c", "test");', {"a.b.c": "test"}),
        ('user_pref("a.b", 1);\nuser_pref("a.c", true);', {"a.b": 1, "a.c": True}),
        ('user_pref("a.b", 1);\n#\nuser_pref("a.c", 1);', {"a.b": 1, "a.c": 1}),
        ("user_pref('a.b.c', '1,2,3,');", {"a.b.c": "1,2,3,"}),
        (
            '\n\nuser_pref("a.b", "1");\n//foo\n\nuser_pref("c.d", "2");\n\n',
            {"a.b": "1", "c.d": "2"},
        ),
        # empty value
        ('user_pref("a.b", "");\n', {"a.b": ""}),
        # invalid value
        ('user_pref("a.b.c", asd);\n', None),
        # unbalanced quotes
        ('user_pref("a, "b");\n', None),
        # unbalanced quotes
        ('user_pref("a", "b);\n', None),
        # missing value
        ('user_pref("a", );\n', None),
        # empty pref name
        ('user_pref("", 0);\n', None),
        # missing pref name
        ("user_pref(, 0);\n", None),
        # unquoted pref name
        ("user_pref(test, 0);\n", None),
    ],
)
def test_adb_process_prefs_to_dict(tmp_path, input_data, result):
    """test ADBProcess.prefs_to_dict()"""
    prefs_js = tmp_path / "prefs.js"
    prefs_js.write_text(input_data)
    assert ADBProcess.prefs_to_dict(prefs_js) == result


def test_adb_process_cpu_usage(mocker):
    """test ADBProcess.cpu_usage()"""
    fake_session = mocker.Mock(spec_set=ADBSession)
    package = "org.test.app"

    # no output
    fake_session.shell.return_value = ADBResult(1, "")
    with ADBProcess(package, fake_session) as proc:
        assert not any(proc.cpu_usage())

    # no entries
    fake_session.shell.return_value = ADBResult(0, "368  0.0 zygote64\n")
    with ADBProcess(package, fake_session) as proc:
        assert not any(proc.cpu_usage())

    # entries (unordered)
    top_output = (
        "368  0.0 zygote64\n"
        " 1042  0.0 webview_zygote\n"
        "11068  3.5 top -b -n 1 -m 20 -q -o PID,%CPU,CMDLINE\n"
        "  571  3.5 system_server\n"
        f"10004  0.0 {package}:tab26\n"
        f"10003  2.1 {package}:gpu\n"
        f"10002  4.1 {package}:crashhelper\n"
        f"10001  54.3 {package}\n"
        "  476  0.0 media.swcodec oid.media.swcodec/bin/mediaswcodec\n"
        "  469  0.0 media.metrics diametrics\n"
        "  468  0.0 media.extractor aextractor\n"
    )
    fake_session.shell.return_value = ADBResult(0, top_output)
    with ADBProcess(package, fake_session) as proc:
        usage = tuple(proc.cpu_usage())
        assert len(usage) == 4
        for pid, cpu in usage:
            if pid == 10001:
                assert cpu == 54.3
            elif pid == 10002:
                assert cpu == 4.1
            elif pid == 10003:
                assert cpu == 2.1
            elif pid == 10004:
                assert cpu == 0
            else:
                raise AssertionError("top output parsing failed")
