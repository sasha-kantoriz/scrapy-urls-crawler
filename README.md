# Scrapy URLs Crawler

## Project structure
Repository contains docker-compose configuration for running `scrapyd` service
and scrapy project with code of URLs crawler spider (`urls_crawler`).

## Project dependencies
For easier usage of developed spider via `scrapyd` service `scrapyd-client` python package was used

## Workflow
To start scrapping websites, please, follow these steps:

### 1. Start `scrapyd` (from the root folder of the repository):
- `docker-compose up -d`

Now you should be able to interact with `scrapyd` service via it's HTTP JSON API
and read all the internals of the `scrapyd` service at the `<project_root>/data` directory

### 2. Deploy scrapy project with spider(s) using `scrapyd-client` library:
- `cd scrapy_project`
- `pip3 install scrapyd-client`
- `scrapyd-deploy --include-dependencies`

From this point new project `scrapy_project` is registered at `scrapyd` service,
please note that all project's spiders are deployed automatically and are available for jobs assignments via their names

### 3. Schedule/List scrapping jobs at `scrapyd` service using provided spider (`urls_crawler`):
- `curl localhost:6800/schedule.json -F project='scrapy_project' -F spider='urls_crawler' -F urls='https://en.wikipedia.org/wiki/Internalpage.html' -F limit='10' -F recursive='1' -F db_host='<DB_HOST>' -F db_port='<DB_PORT>' -F db_name='<DB_NAME>' -F db_password='<DB_PASSWORD>' -F db_user='<DB_USER>'`

### 4. Obtain realtime data of scraping process:
- Jobs logs and all scrapped items are located inside `data` directory of the repo root
- Respective filenames for logs and items can be obtained from `scrapyd` service via `docker-compose logs`
- You'll just need to change files paths, for example `scrapyd` logs for scrapping job scheduled:

`scrapyd_1  | 2023-10-23T07:13:25+0000 [-] Process started:  project='scrapy_project' spider='urls_crawler' job='a74308ce717311ee88fa0242ac160002' pid=79 args=['/usr/bin/python3', '-m', 'scrapyd.runner', 'crawl', 'urls_crawler', '-a', 'db_password=********', '-a', 'urls=https://en.wikipedia.org/wiki/Internalpage.html', '-a', 'db_name=********', '-a', 'recursive=1', '-a', 'db_host=********', '-a', 'db_user=********', '-a', 'db_port=3306', '-a', 'limit=10', '-a', '_job=a74308ce717311ee88fa0242ac160002', '-s', 'LOG_FILE=/var/lib/scrapyd/logs/scrapy_project/urls_crawler/a74308ce717311ee88fa0242ac160002.log', '-s', 'FEEDS={"file:///var/lib/scrapyd/items/scrapy_project/urls_crawler/a74308ce717311ee88fa0242ac160002.jl": {"format": "jsonlines"}}']`

You can access `FEEDS` and `LOG_FILE` just replacing the filepath prefix of `/var/lib/scrapyd` with `data`.