# [ganawaj/coredns-listener](https://git.juanah.cloud/ganawa/coredns-listener)

[![pipeline status](https://git.juanah.cloud/ganawa/coredns-listener/badges/master/pipeline.svg)](https://git.juanah.cloud/ganawa/coredns/-/commits/master)

A webhook listener that updates Corefile & RFC1035 DB files whenever a push is made to
a repository


## Supported Git sites
- Gitlab

## Workflow

When a POST request is recieved at the listener, here is th workflow that is followed:
1. The listener validates that 'X-GITLAB-TOKEN' header matches the configured 'GITLAB_SECRET_TOKEN'
2. The listener ensures that 'X-Gitlab-Event' header is "Push hook"
3. The repository that sent the hook is cloned to a temp directory using the provided credentials
4. Files in directories in the temp directory are copied to the directories 

Simply explained:
```json
"source":"destination"
```

### Further Explained

Say your DNS repository is structured as:

```
+- primary/
   | Corefile
   | db.exmaple.com
   | db.example.org
+- second/
   | Corefile
```

We want the files in the `primary` directory to be copied to our primary CoreDNS server which has all 
of its files located at `/etc/coredns`

Our COREDNS_FILE_MAP json would be structured like this:

```json
"primary":"/etc/coredns"
```

`primary` is a directory from the repo, and `/etc/coredns` corresponds to the CoreDNS config file locations.

If you are running multiple CoreDNS servers with seperate config locations on one server, your COREDNS_FILE_MAP
may look like this: 

```json
"primary":"/etc/primary-dns",
"secondary":"/etc/secondary-dns"
```

Files in the `primary` directory from the repo, would be copied to `/etc/primary-dns`, files in the
`secondary` directory from the repo to `/etc/secondary-dns`

### CoreDNS Corefile suggestions

In order for CoreDNS to apply these changes dynamically without a reload/restart of the server, 
I suggest using the [reload](https://coredns.io/plugins/reload/) and [auto](https://coredns.io/plugins/auto/) plugin

Keep in mind, the serial of your RFC-1035 needs to change in order for it to be reloaded in CoreDNS

Here is an example of my Corefile:
```
(defaults) {
    reload 2s ### reloads Corefile every 2 seconds
    log
    debug
    errors
    prometheus 0.0.0.0:9153
    ready 0.0.0.0:8090
}

. {

  auto {
    directory /etc/coredns ### This should be the directory destination
    reload 2s ### reload every 2 seconds
  }

  import defaults

}

```

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
  ganawa/coredns-listener
```


### docker-compose

```
---
version: "2.1"
services:
  listener:
    image: ganawa/coredns-listener
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
| `-e PUID=1000` | for UserID (optional) |
| `-e PGID=1000` | for GroupID (optional) |
| `-e GITLAB_USERNAME=username` | Username that has the ability to clone repo (optional for public repos) |
| `-e GITLAB_PASSWORD=password` | Password for the user, can be a token (optional for public repos) |
| `-e GITLAB_SECRET_TOKEN=webhook_token` | Gitlab web token |
| `-e COREDNS_FILE_MAP={"primary":"/etc/coredns"}` | json file map, source:destination |
| `-v /etc/coredns` | (optional) Location of CoreDNS config |
