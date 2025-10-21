# Offline mode

The music player has an 'offline mode'. In this mode, the application:

- Does not use a local music library, but synchronizes from a main music server.
- Does not make any connections to the internet, except during synchronisation.
- Keeps a local playback history, which it submits to the main music server when a sync is started.

Example of the offline music player running on a tablet in [a car](https://projects.raphson.nl/projects/tyrone/):

![Music player in dashboard](tyrone_music.jpg)

## Installation

### Container

Install podman (e.g. `apt install podman`)

Create the file `/etc/containers/systemd/music.container` containing:
```
[Container]
ContainerName=music
Image=codeberg.org/raphson/music-server
PublishPort=127.0.0.1:8080:8080
Volume=/var/lib/music-data:/data
Environment=MUSIC_OFFLINE_MODE=1
AutoUpdate=registry

[Install]
WantedBy=default.target
```

Run:
```
systemctl daemon-reload
mkdir /var/lib/music-data
systemctl start music
```

### Pipx

To install the music player in offline mode, run:
```
pipx install 'raphson-mp[offline]'
```

To start the music player in offline mode, use the `--offline` flag. Example: `raphson-mp --offline start`

The container version can also be used in offline mode. Set the environment variable: `MUSIC_OFFLINE_MODE: 1`.

If you want to use the music player in both online and offline mode, you can install both sets of dependencies. Do be careful that you start the offline and online music player using different data directories.
```
pipx install 'raphson-mp[online,offline]'
```

You can create a systemd user service to start the music server on boot.

Create a service file, e.g. `.config/systemd/user/music.service` with the following contents:

```
[Unit]
Description=Music Player

[Service]
ExecStart=/home/youruser/.local/bin/raphson-mp --offline --data-dir /home/youruser/music-data start
Restart=always

[Install]
WantedBy=default.target
```

Don't forget to change the path to the `raphson-mp` executable and the data directory.

Reload: `systemctl --user daemon-reload`

Enable and start the service: `systemctl --user enable --now music`

## Synchronization

To synchronize history and music, visit: http://localhost:8080/offline/sync

If you prefer the command line, or if you want to automate syncing, use: `raphson-mp sync`

## Open music player on boot: PWA

Install chromium-browser (firefox does not support PWA).

Go to http://localhost:8080 and visit the install page to install the music player as a PWA (progressive web app).

Find the corresponding desktop entry in `~/.local/share/applications`, something like `chrome-blahblahblah-Default.desktop`

Make it start on boot: `ln -s ~/.local/share/applications/---.desktop ~/.config/autostart/`

## Open music player on boot: kiosk with desktop

Example to start Firefox on boot:

```
wget -O ~/.local/share/icons/raphson.png https://music.raphson.nl/static/img/raphson.png
mkdir -p ~/.local/share/applications
$EDITOR ~/.local/share/applications/musicplayer.desktop
```

```
[Desktop Entry]
Name=Music Player
Icon=/home/tyrone/.local/share/icons/raphson.png
Exec=firefox --kiosk --new-instance --disable-pinch http://localhost:8080/player
Terminal=false
Type=Application
```
Chromium works as well: `chromium -kiosk http://localhost:8080/player`

Make it start on boot:
```
mkdir -p .config/autostart
ln -s ~/.local/share/applications/musicplayer.desktop .config/autostart/musicplayer.desktop
```

If you use Gnome, you may want to install the [No Overview](https://extensions.gnome.org/extension/4099/no-overview/) extension.

## Open music player on boot: kiosk without desktop

Install a Debian system without desktop.

Install a few packages:
```
apt install lightdm openbox accountsservice
```

Also install firefox or chromium.

Edit `/etc/lightdm/lightdm.conf` with:
```
[Seat:*]
autologin-user=youruser
user-session=openbox
```

In the home directory of *youruser*, create `.config/openbox/autostart` with one of:
 * `firefox --kiosk http://localhost:8080/player`
 * `chromium -kiosk http://localhost:8080/player`

Reboot!
