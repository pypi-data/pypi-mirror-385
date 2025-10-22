# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# pylint: disable=protected-access
from pathlib import Path, PurePosixPath
from subprocess import CompletedProcess, TimeoutExpired
from zipfile import ZipFile

from pytest import mark, raises

from .adb_session import (
    DEVICE_TMP,
    ADBCommandError,
    ADBCommunicationError,
    ADBResult,
    ADBSession,
    ADBSessionError,
    _get_android_sdk,
)


@mark.parametrize(
    "result",
    [
        # success
        (CompletedProcess(["test"], stdout="test\n", returncode=0),),
        # timeout
        TimeoutExpired(["test"], timeout=1),
    ],
)
def test_adb_session_01(mocker, result):
    """test ADBSession._call_adb()"""
    mocker.patch("fxpoppet.adb_session.ADBSession._adb_check", return_value="adb")
    mocker.patch(
        "fxpoppet.adb_session.run",
        autospec=True,
        side_effect=result,
    )
    adb_result = ADBSession._call_adb(["test"], timeout=1)
    if isinstance(result, TimeoutExpired):
        assert adb_result.exit_code == 1
        assert adb_result.output == ""
    else:
        assert adb_result.exit_code == 0
        assert adb_result.output == "test"


@mark.parametrize(
    "ret, msg, exc, connected",
    [
        # not connected
        (None, "ADB session is not connected!", ADBCommunicationError, False),
        # invalid command
        (
            ADBResult(1, "Android Debug Bridge version"),
            "Invalid ADB command 'test'",
            ADBCommandError,
            True,
        ),
        # invalid command
        (ADBResult(1, "adb: usage:"), "adb: usage:", ADBCommandError, True),
        # disconnected device
        (
            ADBResult(1, "error: closed"),
            "Device closed",
            ADBCommunicationError,
            True,
        ),
        # disconnected device
        (
            ADBResult(1, "error: device offline"),
            "Device offline",
            ADBCommunicationError,
            True,
        ),
        # disconnected device
        (
            ADBResult(1, "error: no devices/emulators found"),
            "Device not found",
            ADBCommunicationError,
            True,
        ),
        # success
        (ADBResult(0, "pass"), None, None, True),
        # command failed
        (ADBResult(1, "error msg"), None, None, True),
        # unexpected exit code
        (ADBResult(2, "foo"), None, None, True),
    ],
)
def test_adb_session_02(mocker, ret, msg, exc, connected):
    """test ADBSession.call()"""
    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", return_value=ret)
    session = ADBSession("session-foo")
    session.connected = connected
    if exc is None:
        session._debug_adb = False
        result = session.call(["test"])
        assert result.exit_code == ret.exit_code
        assert result.output == ret.output
    else:
        session._debug_adb = True
        with raises(exc, match=msg):
            session.call(["test"])


def test_adb_session_03(mocker):
    """test ADBSession.devices()"""

    # no devices attached
    def fake_adb_01(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "devices":
            return ADBResult(1, "List of devices attached\n")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_01)
    assert not ADBSession("fake-serial").devices()

    # multiple devices attached
    def fake_adb_02(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "devices":
            return ADBResult(
                0,
                "List of devices attached\n"
                "* daemon not running; starting now at tcp:5037\n"
                "* daemon started successfully\n"
                "emulator-5554   device\n"
                "emulator-5556   offline\n"
                "emulator-5558   device\n",
            )
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_02)
    session = ADBSession("emulator-5558")
    devices = session.devices(any_state=False)
    assert len(devices) == 2
    assert "emulator-5554" in devices
    assert "emulator-5556" not in devices
    assert "emulator-5558" in devices
    assert len(session.devices(any_state=True)) == 3


@mark.parametrize(
    "root, repeat",
    [
        # don't connect
        (False, 0),
        # enable root
        (True, 1),
        # do not enable root
        (False, 1),
        # connect() x2 (already connected)
        (True, 2),
    ],
)
def test_adb_session_04(mocker, root, repeat):
    """test ADBSession.connect() and ADBSession.disconnect()"""
    test_device_id = "492d81f7e1ffee59"

    # pylint: disable=too-many-return-statements
    def fake_adb_call(obj, cmd, **_kw):
        assert cmd
        if cmd[0] == "disconnect":
            if not obj.connected:
                return ADBResult(0, "already disconnected")
            obj.connected = False
            return ADBResult(0, "")
        if cmd[0] == "root":
            obj._root = True
            obj.connected = False
            return ADBResult(0, "restarting adbd as root")
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            if shell_cmd[0] == "getenforce":
                return ADBResult(0, "Permissive")
            if shell_cmd[0] == "getprop" and shell_cmd[1] == "sys.boot_completed":
                return ADBResult(0, "1")
            if shell_cmd[0] == "settings" and shell_cmd[3] == "android_id":
                return ADBResult(0, test_device_id)
            if shell_cmd[0] == "whoami":
                return ADBResult(0, "root" if obj._root else "shell")
        if cmd[0] == "unroot":
            obj._root = False
            obj.connected = False
            return ADBResult(0, "restarting adbd as non root")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    assert not session.connected
    assert session.device_id is None
    assert not session._root
    for _ in range(repeat):
        session.connect(as_root=root)
        assert session.connected
        assert session.device_id == test_device_id
        assert session._root == root
    session.disconnect()
    assert not session.connected
    assert not session._root


@mark.parametrize(
    "android_id, user_id",
    [
        # failed to get android ID
        (ADBResult(1, ""), ADBResult(0, "user")),
        # failed to get user ID
        (ADBResult(0, "1234567890abcdef"), ADBResult(1, "")),
    ],
)
def test_adb_session_05(mocker, android_id, user_id):
    """test ADBSession.connect() device in a bad state"""
    mocker.patch("fxpoppet.adb_session.sleep")

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            if shell_cmd[0] == "getprop" and shell_cmd[1] == "sys.boot_completed":
                return ADBResult(0, "1")
            if shell_cmd[0] == "settings" and shell_cmd[3] == "android_id":
                return android_id
            if shell_cmd[0] == "whoami":
                return user_id
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    with raises(ADBSessionError, match="Device in invalid state"):
        ADBSession("fake-serial").connect()


def test_adb_session_06(mocker):
    """test ADBSession.call() with unknown command"""
    mocker.patch(
        "fxpoppet.adb_session.ADBSession._call_adb",
        return_value=ADBResult(1, "Android Debug Bridge version 1.0.XX"),
    )
    session = ADBSession("fake-serial")
    session.connected = True
    session._root = True
    with raises(ADBCommandError, match="Invalid ADB command 'unknown-cmd'"):
        session.call(["unknown-cmd"])


def test_adb_session_07(tmp_path, mocker):
    """test ADBSession.install()"""

    def fake_get_package_name(*_):
        with (
            ZipFile(apk_file, mode="r") as zfp,
            zfp.open("package-name.txt", "r") as pfp,
        ):
            return pfp.read().strip().decode("utf-8", errors="ignore")

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "install":
            assert cmd[1] == "-g"
            assert cmd[2] == "-r"
            if "test.apk" in cmd[3]:
                return ADBResult(0, "Success")
            return ADBResult(1, "")
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            assert shell_cmd[0] == "pm"
            assert shell_cmd[1] == "grant"
            assert shell_cmd[2] == "test-package.blah.foo"
            return ADBResult(0, "")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    mocker.patch(
        "fxpoppet.adb_session.ADBSession.get_package_name",
        fake_get_package_name,
    )
    session = ADBSession("fake-serial")
    session.connected = True
    # missing apk
    with raises(FileNotFoundError):
        session.install(Path("missing"))
    # bad apk
    pkg_file = tmp_path / "package-name.txt"
    apk_file = tmp_path / "bad.apk"
    pkg_file.write_bytes(b"\n")
    with ZipFile(apk_file, mode="w") as zfp:
        zfp.write(str(pkg_file), "package-name.txt")
    with raises(ADBSessionError, match="Failed to install"):
        session.install(apk_file)
    # good apk
    pkg_file = tmp_path / "package-name.txt"
    apk_file = tmp_path / "test.apk"
    syms_path = tmp_path / "symbols"
    syms_path.mkdir()
    pkg_file.write_bytes(b"test-package.blah.foo\n")
    with ZipFile(apk_file, mode="w") as zfp:
        zfp.write(str(pkg_file), "package-name.txt")
    assert session.install(apk_file)
    # get package name failed
    mocker.patch("fxpoppet.adb_session.ADBSession.get_package_name", return_value=None)
    with raises(ADBSessionError, match="Could not find APK package name"):
        session.install(apk_file)


def test_adb_session_08(mocker):
    """test ADBSession.uninstall()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "uninstall" and cmd[1] == "org.test.preinstalled":
            return ADBResult(0, "Success")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    assert not session.uninstall("org.test.unknown")
    session.connected = True
    assert session.uninstall("org.test.preinstalled")


def test_adb_session_09(mocker):
    """test ADBSession.get_pid()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            if shell_cmd[0] == "pidof":
                if shell_cmd[1] == "org.test.preinstalled":
                    return ADBResult(0, "1337")
                return ADBResult(1, "")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    with raises(ADBCommunicationError, match="ADB session is not connected!"):
        session.get_pid("org.test.unknown")
    session.connected = True
    assert session.get_pid("org.test.unknown") is None
    assert session.get_pid("org.test.preinstalled") == 1337


def test_adb_session_10(mocker):
    """test ADBSession.is_installed()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            if shell_cmd[0] == "pm":
                assert shell_cmd[1] == "list"
                assert shell_cmd[2] == "packages"
                return ADBResult(
                    0,
                    "package:org.mozilla.fennec_aurora\n"
                    "package:org.test.preinstalled\n"
                    "package:com.android.phone\n"
                    "package:com.android.shell",
                )
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    assert not session.is_installed("org.test.unknown")
    assert session.is_installed("org.test.preinstalled")


def test_adb_session_11(mocker):
    """test ADBSession.packages()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            if shell_cmd[0] == "pm":
                assert shell_cmd[1] == "list"
                assert shell_cmd[2] == "packages"
                return ADBResult(
                    0,
                    "package:org.mozilla.fennec_aurora\n"
                    "package:org.test.preinstalled\n"
                    "package:com.android.phone\n"
                    "package:com.android.shell",
                )
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    pkgs = tuple(session.packages)
    assert len(pkgs) == 4
    assert "com.android.phone" in pkgs
    assert "com.android.shell" in pkgs
    assert "org.mozilla.fennec_aurora" in pkgs
    assert "org.test.preinstalled" in pkgs


def test_adb_session_12(mocker):
    """test ADBSession.collect_logs()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "logcat":
            assert cmd[1] == "-d"
            assert cmd[2] == "*:I"
            if len(cmd) == 4:
                assert cmd[-1].startswith("--pid=")
                pid = int(cmd[-1].split("=")[-1])
            else:
                pid = -1
            output = []
            if pid in (-1, 9990):
                output += [
                    "07-27 12:10:15.414  9990  9990 W fake log",
                    "07-27 12:10:15.430  9990  9990 I fake log",
                    "07-27 12:10:15.442  9990  4714 I fake log",
                    "07-27 12:10:15.505  9990  4713 E fake log",
                    "07-27 12:10:15.520  9990  4719 I fake log",
                    "07-27 12:10:15.529  9990  4707 W fake log",
                    "07-27 12:10:15.533  9990  4714 E fake log",
                ]
            if pid == -1:
                output += [
                    "07-27 12:39:27.188  3049  3049 W fake log",
                    "07-27 12:39:27.239  1887  1994 I fake log",
                    "07-27 12:39:27.286  2767  7142 I fake log",
                    "07-27 12:39:27.441  7128  7128 I fake log",
                ]
            return ADBResult(0, "\n".join(output))
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    # test not connected
    assert session.collect_logs() == ""
    # test connected
    session.connected = True
    assert len(session.collect_logs().splitlines()) == 11
    assert len(session.collect_logs(9990).splitlines()) == 7
    assert not session.collect_logs(1111).splitlines()


def test_adb_session_13(mocker):
    """test ADBSession.open_files()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] != "shell":
            raise AssertionError(f"unexpected command {cmd!r}")
        # strip "shell -n -T"
        shell_cmd = cmd[3:]
        if shell_cmd[0] == "lsof":
            if len(shell_cmd) == 3:
                assert shell_cmd[1].startswith("-p")
            return ADBResult(
                0,
                "COMMAND     PID    USER   FD      TYPE   DEVICE  SIZE/OFF"
                "       NODE NAME\n"
                "init          1    root  cwd   unknown                   "
                "            /proc/1/cwd (readlink: Permission denied)\n"
                "lsof      15988   shell  cwd       DIR     0,13       780"
                "       4234 /\n"
                "lsof      15988   shell  txt       REG      8,1    432284"
                "    1696174 /system/bin/toybox\n"
                "lsof      15988   shell    4r      DIR      0,4         0"
                "     120901 /proc/15988/fd\n"
                "a.fennec_  9991  u0_a80   98r      REG      8,1    306672"
                "    1696611 /system/fonts/blah.ttf\n"
                "a.fennec_  9990  u0_a80  cwd       DIR     0,13       780"
                "       4234 /\n"
                "a.fennec_  9990  u0_a80  txt       REG      8,1     17948"
                "    1695879 /system/bin/app_process32\n"
                "a.fennec_  9990  u0_a80  mem   unknown                   "
                "            /dev/ashmem/dalvik-main space (deleted)\n"
                "a.fennec_  9990  u0_a80  mem       CHR    10,58          "
                "       4485 /dev/binder\n"
                "a.fennec_  9990  u0_a80  mem   unknown                   "
                "            /dev/ashmem/dalvik-allocspace zygote / x 0 (deleted)\n"
                "a.fennec_  9990  u0_a80  mem       REG      8,1    152888"
                "    1704079 /system/lib/libexpat.so\n"
                "a.fennec_  9990  u0_a80   54u      REG      8,1    329632"
                "    1769879 /data/data/org.mozilla.fennec_aurora/files/mozilla/a.defau"
                "lt/browser.db-wal\n"
                "a.fennec_  9990  u0_a80   55u     IPv6                0t0"
                "      44549 TCP []:49232->[]:443 (ESTABLISHED)\n"
                "a.fennec_  9990  u0_a80   75w     FIFO      0,9       0t0"
                "      44634 pipe:[44634]\n"
                "a.fennec_  9990  u0_a80   76u     sock                0t0"
                "      44659 socket:[44659]\n"
                "a.fennec_  9990  u0_a80   95u      REG      8,1     98304"
                "    1769930 /data/data/org.mozilla.fennec_aurora/files/mozilla/a.defau"
                "lt/permissions.sqlite\n"
                "a.fennec_  9990  u0_a80   98r      REG      8,1    306672"
                "    1696611 /system/fonts/Roboto-Regular.ttf\n"
                "a.fennec_  9990  u0_a80  122u      CHR    10,59       0t0"
                "       4498 /dev/ashmem\n"
                "a.fennec_  9990  u0_a80  123u     IPv4                0t0"
                "      44706 UDP :1900->:0\n"
                "a.fennec_  9990  u0_a80  125u     0000     0,10       0t0"
                "       3655 anon_inode:[eventpoll]\n"
                "a.fennec_  9990  u0_a80  126u     IPv4                0t0"
                "      44773 TCP :58190->:443 (ESTABLISHED)\n"
                "a.fennec_  9990  u0_a80  128u     unix                0t0"
                "      44747 socket\n"
                "a.fennec_  9990  u0_a80  130u     IPv4                0t0"
                "      44840 TCP :35274->:443 (SYN_SENT)\n",
            )
        if shell_cmd[0] == "ps":
            assert "--ppid" in shell_cmd
            assert "9990" in shell_cmd
            return ADBResult(
                0,
                "PID   PPID  RSS  NAME\n9991  9990  3331 org.mozilla.fennec_aurora\n",
            )
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    # list all open files
    assert len(tuple(session.open_files())) == 7
    # list process specific open files
    assert len(tuple(session.open_files(pid=9990))) == 5
    # list process and children specific open files
    assert len(tuple(session.open_files(pid=9990, children=True))) == 6
    with raises(AssertionError):
        tuple(session.open_files(pid=None, children=True))
    # list open files with "files" args for coverage
    assert any(session.open_files(files=["test"]))


def test_adb_session_14(mocker):
    """test ADBSession._get_procs()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            if shell_cmd[0] == "ps":
                output = ["PID   PPID  RSS  NAME\n"]
                if shell_cmd[-1] == "-A":
                    output += [
                        "1     0     2208   /init\n",
                        "a     a     a      invalid.for.coverage\n",
                        "1242  2     0      kswapd0\n",
                        "1337  1772  1024   org.test.preinstalled\n",
                        "1338  1337  1024   org.test.child\n",
                        "1772  1     122196 zygote\n",
                        "2158  1758  0      sdcard\n",
                        "1773  1     9624   /system/bin/audioserver\n",
                        "5847  1     2348   /sbin/adbd\n",
                        "9990  1772  128064 org.mozilla.fennec_aurora\n",
                        "5944  5847  6280   ps\n",
                    ]
                elif "--ppid" in shell_cmd:
                    output.append("9991  9990  3332   org.mozilla.fennec_aurora\n")
                else:
                    output.append("9990  1772  128064 org.mozilla.fennec_aurora\n")
                return ADBResult(0, "".join(output))
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    assert len(tuple(session._get_procs())) == 10
    dev_procs = tuple(session._get_procs(pid=9990))
    assert len(dev_procs) == 1
    assert dev_procs[0].pid == 9990
    dev_procs = tuple(session._get_procs(pid_children=9990))
    assert len(dev_procs) == 1
    assert dev_procs[0].pid == 9991


def test_adb_session_15(tmp_path, mocker):
    """test ADBSession.push()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "push":
            assert "test.txt" in cmd[1]
            assert cmd[2] == "dst"
            return ADBResult(0, " pushed. ")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    with raises(FileNotFoundError):
        session.push(Path("not_a_file"), "dst")
    push_file = tmp_path / "test.txt"
    push_file.write_bytes(b"test\n")
    assert session.push(push_file, "dst")


def test_adb_session_16(mocker):
    """test ADBSession.pull()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "pull":
            assert cmd[1] == "src"
            assert cmd[2] == "dst"
            return ADBResult(0, " pulled. ")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    assert session.pull("src", "dst")


def test_adb_session_17(mocker):
    """test ADBSession.clear_log()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "logcat":
            assert cmd[1] == "--clear"
            return ADBResult(0, "")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    assert session.clear_logs()


def test_adb_session_18(mocker):
    """test ADBSession.listdir()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            if shell_cmd[0] == "ls":
                assert shell_cmd[1] == "-A"
                if shell_cmd[2] == "missing-dir":
                    return ADBResult(1, "")
                return ADBResult(0, "test")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    with raises(FileNotFoundError):
        session.listdir("missing-dir")
    dir_list = tuple(str(x) for x in session.listdir("fake-dir"))
    assert len(dir_list) == 1
    assert "test" in dir_list


def test_adb_session_19(mocker):
    """test ADBSession.process_exists()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            if shell_cmd[0] == "ps":
                assert "9990" in shell_cmd
                return ADBResult(0, "PID\n9990\n\n")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    assert session.process_exists(9990)


def test_adb_session_20(mocker, tmp_path):
    """test ADBSession._aapt_check()"""
    (tmp_path / "android-9").mkdir()
    fake_aapt_sys = tmp_path / "android-9" / "aapt-sys"
    fake_aapt_sys.touch()
    fake_aapt = tmp_path / "android-9" / "aapt"
    fake_aapt.touch()
    # use system aapt
    mocker.patch("fxpoppet.adb_session.AAPT_BIN", None)
    mocker.patch("fxpoppet.adb_session.ANDROID_SDK_ROOT", tmp_path / "missing")
    mocker.patch("fxpoppet.adb_session.which", return_value=str(fake_aapt_sys))
    assert ADBSession._aapt_check() == str(fake_aapt_sys)
    # use recommended aapt
    mocker.patch("fxpoppet.adb_session.AAPT_BIN", None)
    mocker.patch("fxpoppet.adb_session.ANDROID_SDK_ROOT", tmp_path)
    assert ADBSession._aapt_check() == str(fake_aapt)
    # aapt not installed
    mocker.patch("fxpoppet.adb_session.AAPT_BIN", None)
    mocker.patch("fxpoppet.adb_session.ANDROID_SDK_ROOT", tmp_path / "missing")
    mocker.patch("fxpoppet.adb_session.which", return_value=None)
    with raises(OSError, match=r"Please install AAPT"):
        assert ADBSession._aapt_check()


def test_adb_session_21(mocker, tmp_path):
    """test ADBSession._adb_check()"""
    mocker.patch("fxpoppet.adb_session.sleep")
    (tmp_path / "platform-tools").mkdir()
    fake_adb_sys = tmp_path / "platform-tools" / "adb-sys"
    fake_adb_sys.touch()
    fake_adb = tmp_path / "platform-tools" / "adb"
    fake_adb.touch()
    # use system adb
    mocker.patch("fxpoppet.adb_session.ADB_BIN", None)
    mocker.patch("fxpoppet.adb_session.ANDROID_SDK_ROOT", tmp_path / "missing")
    mocker.patch("fxpoppet.adb_session.which", return_value=str(fake_adb_sys))
    assert ADBSession._adb_check() == str(fake_adb_sys)
    # use recommended adb
    mocker.patch("fxpoppet.adb_session.ADB_BIN", None)
    mocker.patch("fxpoppet.adb_session.ANDROID_SDK_ROOT", tmp_path)
    assert ADBSession._adb_check() == str(fake_adb)
    # adb not installed
    mocker.patch("fxpoppet.adb_session.ADB_BIN", None)
    mocker.patch("fxpoppet.adb_session.ANDROID_SDK_ROOT", tmp_path / "missing")
    mocker.patch("fxpoppet.adb_session.which", return_value=None)
    with raises(OSError, match=r"Please install ADB"):
        assert ADBSession._adb_check()


def test_adb_session_22(mocker, tmp_path):
    """test ADBSession.get_package_name()"""
    mocker.patch(
        "fxpoppet.adb_session.ADBSession._aapt_check", return_value=b"fake_aapt"
    )
    mocker.patch("fxpoppet.adb_session.check_output", return_value=b"")
    with raises(FileNotFoundError):
        ADBSession.get_package_name(Path("/fake/path"))
    fake_apk = tmp_path / "fake.apk"
    fake_apk.touch()
    assert ADBSession.get_package_name(fake_apk) is None
    output = (
        b"package: name='org.mozilla.fennec_aurora' versionCode='2015624653'"
        b" versionName='68.0a1' platformBuildVersionName=''\n"
        b"install-location:'internalOnly'\n"
        b"sdkVersion:'16'\n"
        b"targetSdkVersion:'28'\n"
        b"uses-permission: name='android.permission.READ_SYNC_SETTINGS'\n"
        b"uses-permission:"
        b" name='org.mozilla.fennec_aurora_fxaccount.permission.PER_ACCOUNT_TYPE'\n"
        b"application-label:'Firefox Nightly'\n"
        b"application-label-en-GB:'Firefox Nightly'\n"
        b"application-icon-240:'res/mipmap-anydpi-v26/ic_launcher.xml'\n"
        b"application-icon-65535:'res/mipmap-anydpi-v26/ic_launcher.xml'\n"
        b"application:"
        b" label='Firefox Nightly' icon='res/mipmap-anydpi-v26/ic_launcher.xml'\n"
        b"application-debuggable\n"
        b"feature-group: label=''\n"
        b"  uses-gl-es: '0x20000'\n"
        b"  uses-feature-not-required: name='android.hardware.audio.low_latency'\n"
        b"  uses-feature: name='android.hardware.touchscreen'\n"
        b"  uses-feature: name='android.hardware.location.network'\n"
        b"  uses-implied-feature: name='android.hardware.location.network'"
        b" reason='requested android.permission.ACCESS_COARSE_LOCATION permission'\n"
        b"  uses-feature: name='android.hardware.wifi'\n"
        b"  uses-implied-feature: name='android.hardware.wifi'"
        b" reason='requested android.permission.ACCESS_WIFI_STATE permission, and"
        b" requested android.permission.CHANGE_WIFI_STATE permission'\n"
        b"provides-component:'app-widget'\n"
        b"main\n"
        b"other-activities\n"
        b"other-receivers\n"
        b"other-services\n"
        b"supports-screens: 'small' 'normal' 'large' 'xlarge'\n"
        b"supports-any-density: 'true'\n"
        b"locales: '--_--' 'ca' ' 'en-GB' 'zh-HK' 'zh-CN' 'en-IN' 'pt-BR' 'es-US'"
        b" 'pt-PT' 'en-AU' 'zh-TW'\n"
        b"densities: '120' '160' '240' '320' '480' '640' '65534' '65535'\n"
        b"native-code: 'x86'"
    )
    mocker.patch("fxpoppet.adb_session.check_output", return_value=output)
    assert ADBSession.get_package_name(fake_apk) == "org.mozilla.fennec_aurora"


def test_adb_session_23(mocker):
    """test ADBSession.get_enforce()"""
    mocker.patch(
        "fxpoppet.adb_session.ADBSession.call", return_value=ADBResult(0, "Enforcing")
    )
    session = ADBSession("fake-serial")
    assert session.get_enforce()
    mocker.patch(
        "fxpoppet.adb_session.ADBSession.call", return_value=ADBResult(0, "Blah")
    )
    session = ADBSession("fake-serial")
    assert not session.get_enforce()


def test_adb_session_24(mocker):
    """test ADBSession.set_enforce()"""
    # disable when enabled
    fake_call = mocker.patch("fxpoppet.adb_session.ADBSession.call")
    mocker.patch("fxpoppet.adb_session.ADBSession.get_enforce", return_value=True)
    session = ADBSession("fake-serial")
    session.set_enforce(0)
    assert fake_call.call_count == 1
    fake_call.reset_mock()
    # enable when disabled
    mocker.patch("fxpoppet.adb_session.ADBSession.get_enforce", return_value=False)
    session = ADBSession("fake-serial")
    session.set_enforce(1)
    assert fake_call.call_count == 1


def test_adb_session_25(mocker):
    """test ADBSession.realpath()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            if shell_cmd[0] == "realpath":
                if shell_cmd[1] == "missing/path":
                    return ADBResult(1, "")
                return ADBResult(0, "existing/path")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    with raises(FileNotFoundError):
        session.realpath(PurePosixPath("missing/path"))
    assert str(session.realpath(PurePosixPath("existing/path"))) == "existing/path"


def test_adb_session_26(mocker):
    """test ADBSession.reverse()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "reverse":
            return ADBResult(0, "")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    assert session.reverse(1234, 1235)


def test_adb_session_27(mocker):
    """test ADBSession.reverse_remove()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "reverse":
            if cmd[1] == "--remove":
                assert cmd[2].startswith("tcp:")
            elif cmd[1] == "--remove-all":
                pass
            else:
                raise AssertionError(f"unexpected command {cmd!r}")
            return ADBResult(0, "")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    assert session.reverse_remove()
    assert session.reverse_remove(remote=1025)


def test_adb_session_28(mocker):
    """test ADBSession.airplane_mode()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "shell":
            # strip "shell -n -T"
            shell_cmd = cmd[3:]
            if shell_cmd[0] == "settings":
                if shell_cmd[1] == "get":
                    assert shell_cmd[2] == "global"
                    assert shell_cmd[3] == "airplane_mode_on"
                    return ADBResult(0, "1")
                if shell_cmd[1] == "put":
                    assert shell_cmd[2] == "global"
                    assert shell_cmd[3] == "airplane_mode_on"
                    assert shell_cmd[4] in "01"
                    return ADBResult(0, "")
            if shell_cmd[0] == "su":
                assert shell_cmd[1] == "root"
                assert shell_cmd[2] == "am"
                assert shell_cmd[3] == "broadcast"
                assert shell_cmd[4] == "-a"
                assert shell_cmd[5] == "android.intent.action.AIRPLANE_MODE"
                return ADBResult(0, "")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    session = ADBSession("fake-serial")
    session.connected = True
    session.airplane_mode = False
    session.airplane_mode = True
    assert session.airplane_mode


@mark.parametrize(
    "result, shell_effect",
    [
        # successful boot
        (True, (ADBResult(0, "0"), ADBResult(0, "1"))),
        # timeout
        (False, (ADBResult(0, "0"), ADBResult(0, "0"))),
    ],
)
def test_adb_session_29(mocker, result, shell_effect):
    """test ADBSession.wait_for_boot()"""
    mocker.patch("fxpoppet.adb_session.time", side_effect=range(3))
    mocker.patch.object(ADBSession, "shell", side_effect=shell_effect)
    session = ADBSession("fake-serial")
    session.connected = True
    assert session.wait_for_boot(timeout=2, poll_wait=0) == result


def test_adb_session_30(mocker):
    """test ADBSession.reboot_device()"""

    def fake_adb_call(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "reboot":
            return ADBResult(0, "")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_call)
    mocker.patch("fxpoppet.adb_session.ADBSession.connect", spec=True)
    session = ADBSession("fake-serial")
    session.connected = True
    with raises(AssertionError):
        session.reboot_device()


def test_adb_session_31(mocker):
    """test ADBSession.remount()"""

    def fake_adb_01(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "remount":
            return ADBResult(0, "Permission denied")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_01)
    session = ADBSession("fake-serial")
    session.connected = True
    session._root = True
    with raises(ADBSessionError):
        session.remount()

    def fake_adb_02(_, cmd, **_kw):
        assert cmd
        if cmd[0] == "remount":
            return ADBResult(0, "")
        raise AssertionError(f"unexpected command {cmd!r}")

    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", fake_adb_02)
    session = ADBSession("fake-serial")
    session.connected = True
    # test as non-root
    with raises(AssertionError):
        session.remount()
    session._root = True
    # test as root
    session.remount()


def test_adb_session_32(mocker):
    """test ADBSession.sanitizer_options()"""
    mocker.patch("fxpoppet.adb_session.ADBSession.call", autospec=True)

    def fake_install_file(_, src, dst, **_kw):
        src = Path(src)
        assert src.name == "asan.options.gecko"
        assert src.read_text(encoding="ascii") in ("a=1:b=2", "b=2:a=1")
        assert str(dst) == str(DEVICE_TMP)

    mocker.patch("fxpoppet.adb_session.ADBSession.install_file", fake_install_file)
    session = ADBSession("fake-serial")
    session.sanitizer_options("asan", {"a": "1", "b": "2"})


def test_adb_session_33(mocker):
    """test ADBSession.install_file()"""
    mocker.patch("fxpoppet.adb_session.ADBSession.push", autospec=True)
    mocker.patch("fxpoppet.adb_session.ADBSession.shell", autospec=True)
    session = ADBSession("fake-serial")
    session.install_file(
        Path("a/b"), PurePosixPath("/sdcard"), mode="777", context="foo"
    )


def test_adb_session_34(mocker):
    """test ADBSession.connect() timeout"""
    mocker.patch("fxpoppet.adb_session.ADBSession.wait_for_boot", return_value=False)
    mocker.patch("fxpoppet.adb_session.ADBSession.call", return_value=ADBResult(0, ""))
    mocker.patch(
        "fxpoppet.adb_session.ADBSession.devices",
        return_value={"fake-serial": "device"},
    )
    with raises(ADBCommunicationError, match="Device boot timeout exceeded"):
        ADBSession("fake-serial").connect(boot_timeout=1)


def test_adb_session_35(mocker):
    """test ADBSession.connect() set enforce failed"""
    mocker.patch("fxpoppet.adb_session.ADBSession.wait_for_boot")
    mocker.patch("fxpoppet.adb_session.ADBSession.get_enforce")
    mocker.patch("fxpoppet.adb_session.ADBSession.call", return_value=ADBResult(0, ""))
    mocker.patch(
        "fxpoppet.adb_session.ADBSession.shell", return_value=ADBResult(0, "root")
    )
    mocker.patch(
        "fxpoppet.adb_session.ADBSession.devices",
        return_value={"fake-serial": "device"},
    )
    with raises(ADBSessionError, match=r"set_enforce\(0\) failed!"):
        ADBSession("fake-serial").connect(as_root=True, boot_timeout=1)


def test_adb_session_36(mocker):
    """test ADBSession.connect() root login failed"""
    mocker.patch("fxpoppet.adb_session.ADBSession.wait_for_boot")
    mocker.patch("fxpoppet.adb_session.ADBSession.call", return_value=ADBResult(0, ""))
    mocker.patch(
        "fxpoppet.adb_session.ADBSession.shell", return_value=ADBResult(0, "user")
    )
    mocker.patch(
        "fxpoppet.adb_session.ADBSession.devices",
        return_value={"fake-serial": "device"},
    )
    with raises(ADBSessionError, match=r"Root login failed"):
        ADBSession("fake-serial").connect(as_root=True, boot_timeout=1)


@mark.parametrize(
    "effect",
    [
        # failed
        (ADBResult(1, ""),),
        # not supported
        ADBCommandError("Invalid ADB command ..."),
    ],
)
def test_adb_session_37(mocker, effect):
    """test ADBSession.disconnect() unroot"""
    mocker.patch("fxpoppet.adb_session.ADBSession._call_adb", side_effect=effect)
    session = ADBSession("fake-serial")
    session.connected = True
    session._root = True
    session.disconnect()
    assert not session.connected


@mark.parametrize(
    "env_var, os_name",
    [
        ("ANDROID_HOME", "Linux"),
        ("ANDROID_SDK_ROOT", "Linux"),
        ("LOCALAPPDATA", "Windows"),
        (None, "Darwin"),
        # default to ~/
        (None, "Linux"),
    ],
)
def test_adb_get_android_sdk_01(mocker, tmp_path, env_var, os_name):
    """test ADBSession._get_android_sdk()"""

    def _getenv(in_var, default=None):
        if in_var == env_var:
            return str(tmp_path)
        return default

    mocker.patch("fxpoppet.adb_session.getenv", _getenv)
    mocker.patch("fxpoppet.adb_session.system", return_value=os_name)
    assert _get_android_sdk()
