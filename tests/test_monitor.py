import psutil
from unittest.mock import MagicMock, patch

from monitor import stats


def test_cpu_returns_formatted_string():
    with patch('psutil.cpu_percent', return_value=42.5), patch('psutil.cpu_count', return_value=8):
        output = stats.cpu()
    assert output == "CPU: 42.5%  |  Cores: 8"


def test_mem_returns_formatted_string():
    mock_mem = MagicMock(total=8 * 1024**3, used=2 * 1024**3, percent=25.0)
    with patch('psutil.virtual_memory', return_value=mock_mem):
        output = stats.mem()
    assert output == "Memory: 2.00 GB / 8.00 GB  (25.0%)"


def test_disk_returns_formatted_string():
    mock_disk = MagicMock(total=100 * 1024**3, used=40 * 1024**3, percent=40.0)
    with patch('psutil.Process') as mock_process, patch('psutil.disk_usage', return_value=mock_disk):
        mock_process.return_value.cwd.return_value = '/tmp'
        output = stats.disk()
    assert output == "Disk: 40.00 GB / 100.00 GB  (40.0%)"


def test_ps_returns_table():
    proc1 = MagicMock()
    proc1.info = {'pid': 1, 'name': 'alpha', 'cpu_percent': 10.0, 'memory_info': MagicMock(rss=1024)}
    proc2 = MagicMock()
    proc2.info = {'pid': 2, 'name': 'beta', 'cpu_percent': 20.0, 'memory_info': MagicMock(rss=2048)}

    with patch('psutil.process_iter', return_value=[proc1, proc2]):
        table = stats.ps(top_n=2)

    lines = table.splitlines()
    assert lines[0].startswith('PID')
    assert 'beta' in lines[1]
    assert lines[1].startswith('2')
    assert '1.00 KB' in lines[2]
