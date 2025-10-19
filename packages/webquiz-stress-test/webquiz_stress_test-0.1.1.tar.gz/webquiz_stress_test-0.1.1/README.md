# WebQuiz Stress Test

Performance testing tool for [WebQuiz](https://github.com/oduvan/webquiz) servers - simulate concurrent users taking quizzes to measure server performance, identify bottlenecks, and validate scalability.

## Features

- **Concurrent client simulation**: Async execution with configurable number of clients
- **Realistic user behavior**: Random delays between answers, optional page reloads, registration updates
- **Randomized quiz support**: Automatically follows server-provided question order for each client
- **Approval workflow testing**: Supports both auto-approved and manual approval scenarios
- **Detailed statistics**: Response times (min/avg/max/median), success rates, error tracking
- **Request breakdown**: Separate stats for register, verify, submit answer, and approve operations
- **Multiple installation options**: PyPI package, standalone binaries, or from source

## Quick Start

### Installation

**Option 1: Install from PyPI (recommended)**
```bash
pip install webquiz-stress-test
webquiz-stress-test --help
```

**Option 2: Download pre-built binary**

Download the latest binary for your platform from [Releases](https://github.com/oduvan/webquiz-stress-test/releases):
- **Linux**: `webquiz-stress-test-linux.zip`
- **macOS Intel**: `webquiz-stress-test-macos-intel.zip`
- **macOS Apple Silicon**: `webquiz-stress-test-macos-apple-silicon.zip`
- **Windows**: `webquiz-stress-test-windows.exe.zip`

```bash
# Linux/macOS example
unzip webquiz-stress-test-linux.zip
chmod +x webquiz-stress-test-linux
./webquiz-stress-test-linux --help
```

**Option 3: Install from source**
```bash
git clone https://github.com/oduvan/webquiz-stress-test.git
cd webquiz-stress-test
poetry install
poetry run webquiz-stress-test --help
```

### Basic Usage

```bash
# Test with 10 concurrent users (default)
webquiz-stress-test

# Heavy load test with 100 users
webquiz-stress-test -c 100

# Test custom server with specific delays
webquiz-stress-test -u http://localhost:9000 --delay-min 0.2 --delay-max 1.5

# Test with approval workflow
webquiz-stress-test --wait-for-approval -k your_master_key
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-u, --url` | Server URL | `http://localhost:8080` |
| `-c, --clients` | Number of concurrent clients | `10` |
| `--delay-min` | Minimum delay between answers (seconds) | `0.5` |
| `--delay-max` | Maximum delay between answers (seconds) | `2.0` |
| `--reload-prob` | Page reload probability (0.0-1.0) | `0.1` |
| `--update-registration-prob` | Registration update probability (0.0-1.0) | `0.2` |
| `--wait-for-approval` | Enable approval workflow testing | `false` |
| `--no-wait-for-approval` | Don't wait for approval (assume auto-approved) | N/A |
| `-k, --master-key` | Master key for admin operations | None |
| `--approval-timeout` | Approval wait timeout (seconds) | `30.0` |

## Usage Examples

### Load Testing

**Test with 50 concurrent users:**
```bash
webquiz-stress-test -c 50 --delay-min 0.3 --delay-max 1.0
```

**Rapid-fire test (minimal delays):**
```bash
webquiz-stress-test -c 100 --delay-min 0.1 --delay-max 0.3
```

### Realistic Behavior Simulation

**Test with frequent page reloads (30% probability):**
```bash
webquiz-stress-test --reload-prob 0.3
```

**Test with high registration update rate:**
```bash
webquiz-stress-test --update-registration-prob 0.5
```

### Approval Workflow Testing

**Test approval workflow (requires admin to approve users manually):**
```bash
# Terminal 1: Start WebQuiz server with master key
webquiz --master-key test123

# Terminal 2: Run stress test with approval workflow
webquiz-stress-test --wait-for-approval -k test123
```

## Output Example

```
============================================================
WebQuiz Stress Test
============================================================
Server URL: http://localhost:8080
Number of clients: 50
Answer delay range: 0.5s - 2.0s
Reload probability: 10.0%
Update registration probability: 20.0%
Wait for approval: False
============================================================

[Client 1] Registered as StressTest_User_1_1234567890 (user_id: 123456)
[Client 2] Registered as StressTest_User_2_1234567890 (user_id: 789012)
...

Overall Statistics:
  Duration: 45.23s
  Clients Started: 50
  Clients Completed: 48
  Clients Failed: 2
  Completion Rate: 96.00%

Request Statistics:
------------------------------------------------------------

Register:
  Total Requests: 50
  Success: 50
  Failures: 0
  Success Rate: 100.00%
  Avg Response Time: 0.025s
  Min Response Time: 0.015s
  Max Response Time: 0.089s
  Median Response Time: 0.023s

Submit Answer:
  Total Requests: 480
  Success: 476
  Failures: 4
  Success Rate: 99.17%
  Avg Response Time: 0.018s
  Min Response Time: 0.010s
  Max Response Time: 0.156s
  Median Response Time: 0.016s
```

## How It Works

The stress test simulates realistic user behavior:

1. **Registration**: Each client registers with a unique username
2. **Optional Updates**: Some clients update their registration (configurable probability)
3. **Approval Wait** (optional): If approval workflow is enabled, clients wait for admin approval
4. **Quiz Taking**: Clients fetch quiz metadata and answer all questions sequentially
5. **Random Delays**: Configurable delays between answers to simulate thinking time
6. **Page Reloads**: Optional page reloads to simulate real user behavior
7. **Statistics Collection**: All requests are timed and success/failure rates tracked

### Supported Features

- **Randomized quizzes**: Follows server-provided `question_order` for each client
- **Sequential answering**: Enforces server-side validation for randomized quizzes
- **Approval workflow**: Supports both manual and auto-approval modes
- **Session persistence**: Maintains cookies across requests
- **Error handling**: Graceful handling of network errors and timeouts

## Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/oduvan/webquiz-stress-test.git
cd webquiz-stress-test

# Install dependencies
poetry install

# Run from source
poetry run webquiz-stress-test -c 10
```

### Building Binary

```bash
# Build binary for current platform
poetry run build_binary

# Binary will be created at:
./dist/webquiz-stress-test

# Run the binary
./dist/webquiz-stress-test --help
```

## Requirements

- Python 3.9+
- aiohttp (automatically installed)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Related Projects

- [WebQuiz](https://github.com/oduvan/webquiz) - The quiz server this tool is designed to test

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
- Check existing [GitHub Issues](https://github.com/oduvan/webquiz-stress-test/issues)
- Create a new issue with details about your problem
- Include server version, stress test version, and command used
