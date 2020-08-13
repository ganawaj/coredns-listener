# [ganawaj/coredns-listener](https://git.juanah.cloud/ganawa/coredns-listener)

[![pipeline status](https://git.juanah.cloud/ganawa/coredns-listener/badges/master/pipeline.svg)](https://git.juanah.cloud/ganawa/coredns/-/commits/master)

A webhook listener that updates Corefile & RFC1035 DB files whenever a push is made to
a repository. Currently only supports Gitlab.

## Workflow

When a POST request is recieved at the listener, here is th workflow that is followed:
1. The listener validates that 'X-GITLAB-TOKEN' header matches the configured 'GITLAB_SECRET_TOKEN'
2. The listener ensures that 'X-Gitlab-Event' header is "Push hook"
3. The repository that sent the hook is cloned to a temp directory using the provided credentials


## Usage

Here are some examples to create the container.

### docker

```
docker create \
  --name=coredns-listener \
  -e PUID=1000 \
  -e PGID=1000 \
  -p 5000:5000 \
  -v /path/to/coredns/config:/etc/coredns \
  --restart unless-stopped \
  ganawaj/coredns-listener
```


### docker-compose

```
---
version: "2.1"
services:
  listener:
    image: ganawaj/coredns-listener
    container_name: coredns-listener
    environment:
      - PUID=1000
      - PGID=1000
      - GITLAB_USERNAME=username
      - GITLAB_PASSWORD=password
      - GITLAB_SECRET_TOKEN=webhook_token
      - COREDNS_FILE_MAP={"primary":"/etc/coredns"}
    volumes:
      - /path/to/coredns/config:/etc/coredns
    ports:
      - 5000:5000
    restart: unless-stopped
```

## Parameters

Container images are configured using parameters passed at runtime (such as those above). These parameters are separated by a colon and indicate `<external>:<internal>` respectively. For example, `-p 8080:80` would expose port `80` from inside the container to be accessible from the host's IP on port `8080` outside the container.

| Parameter | Function |
| :----: | --- |
| `-p 5000` | The port for the webhook to listen on |
| `-e PUID=1000` | for UserID |
| `-e PGID=1000` | for GroupID |
| `-e TZ=Europe/London` | Specify a timezone to use EG Europe/London, this is required for Sonarr |
| `-e UMASK_SET=022` | control permissions of files and directories created by Sonarr |
| `-v /config` | Database and sonarr configs |
| `-v /tv` | Location of TV library on disk (See note in Application setup) |
| `-v /downloads` | Location of download managers output directory (See note in Application setup) |
