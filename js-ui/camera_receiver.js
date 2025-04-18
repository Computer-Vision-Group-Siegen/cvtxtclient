async function request(address, apiKey, path, method = "GET", body = undefined) {
    const response = await fetch("http://"+address+"/api/v1/"+path, {
        method: method,
        headers: { "Content-Type": "application/json", "accept": "application/json", "X-API-KEY": apiKey },
        body: body?JSON.stringify(body):undefined,
    });
    return response;
}

self.onmessage = async function({data}) {
    await request(data.address, data.apiKey, "controller/camera/start", "POST", { width: 320, height: 240, fps: 15, rotate: false, debug: false });
    const response = await request(data.address, data.apiKey, "controller/camera/image-stream?X-API-KEY=" + data.apiKey);
    const reader = response.body.getReader();
    let frame = [];
    while (true) {
        const { value, done } = await reader.read();
        if (done) {
            break;
        }
        for (let i = 0; i < value.length; i++) {
            let isBoundary = false;
            if (value[i] == 45) {
                isBoundary = true;
                for (let j = 0; j < 7; j++) {
                    if (value[i+j] !== [45,45,102,114,97,109,101][j]) {
                        isBoundary = false;
                        break;
                    }
                }
            }
            if (isBoundary && frame.length > 0) {
                self.postMessage(URL.createObjectURL(new Blob([new Uint8Array(frame).slice(36).buffer], { type: "image/jpeg" })));
                frame = [];
            } else {
                frame.push(value[i]);
            }
        }
    }
}