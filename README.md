# NHoax Proxy

HTTP proxy companion service that checks whether URLs are malicious.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
git clone https://github.com/lmontanares/nhoax-proxy.git
cd nhoax-proxy
make install
```

## Usage

Start the server:

```bash
make run
```

Check a URL:

```
GET /urlinfo/1/{hostname_and_port}/{path}
```

Example:

```bash
curl http://localhost:8000/urlinfo/1/bad.com:8080/virus/download
# {"safe": false}
```

Seed the database from a CSV file with a `url` column:

```bash
make seed               # uses data/urls.csv
make seed CSV=my.csv    # custom file
```

## Development

```bash
make test
```
