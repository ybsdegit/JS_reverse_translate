function createGuid() {
    return (((1 + Math.random()) * 65536) | 0).toString(16).substring(1)
}

var guid = createGuid() + createGuid() + "-" + createGuid() + "-" + createGuid() + createGuid() + "-" + createGuid() + createGuid() + createGuid();
    // return createGuid() + createGuid() + "-" + createGuid() + "-" + createGuid() + createGuid() + "-" + createGuid() + createGuid() + createGuid();
    // return guid