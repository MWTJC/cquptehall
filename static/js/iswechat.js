function is_weixn() {
    var ua = navigator.userAgent.toLowerCase();
    return ua.match(/MicroMessenger/i) === "micromessenger";
}