#!/bin/bash -e
main() {
    local username="${SSH_AUTH_USER:-default}"
    local home
    home=$(mk_home "$username")
    setup_passwd "$username" "$home"
}
mk_home() {
    local username="${1:?}"
    mkdir -p "/tmp/home/$username" && \
    echo "/tmp/home/$username" && \
    return 0
    mktemp --tmpdir -d "${username}.XXXXXX"
}
setup_passwd() {
    local username="${1:?}"
    local home="${2:?}"
    local uid="$(id -u)"
    local gid="${3:-0}"
    local passwd=/etc/passwd

    ! getent passwd $uid 2>/dev/null || return 0
    if ! [[ -w "$passwd" ]]; then
        echo "There is no permission to add user $username to $passwd"
        return 0
    fi
    [[ "$uid" ]] || uid="$(id -u)"
    echo \
        "${username}:x:${uid}:${gid}:Default Application User:${home}:/sbin/nologin" \
        >> /etc/passwd
}
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
