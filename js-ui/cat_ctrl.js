const connectForm = document.getElementById("connect-form");
const addressTextfield = document.getElementById("connect-form-address");
const apiKeyTextfield = document.getElementById("connect-form-key");
const statusLabel = document.getElementById("connect-form-status");
const submitButton = document.getElementById("connect-form-submit");
const cameraView = document.getElementById("camera-img");
//const robotStatusView = document.getElementById("robot-status");
/*const moveJoystick = document.getElementById("move-joystick");
const lookJoystick = document.getElementById("look-joystick");*/
//const centerDot = document.getElementById("center-dot");
/*const messageInput = document.getElementById("msg-input");
const messageSend = document.getElementById("msg-send");*/

const pressedKeys = new Set();
/*let draggingLookJoystick = false;
let draggingMoveJoystick = false;*/
//let draggingScreen = false;

const cameraReceiver = new Worker("camera_receiver.js");

let deltaTrans = {x: 0.0, y: 0.0};
let deltaRot = 0;

function vAdd(a, b) {
    return {x: a.x+b.x, y: a.y+b.y};
}

function vSub(a, b) {
    return {x: a.x-b.x, y: a.y-b.y};
}

function vLen(a) {
    return Math.sqrt(a.x*a.x+a.y*a.y);
}

function vAng(a) {
    return -Math.atan2(a.y, a.x);
}

async function request(address, apiKey, path, method = "GET", body = undefined) {
    try {
        const response = await fetch("http://"+address+"/api/v1/"+path, {
            method: method,
            headers: { "Content-Type": "application/json", "accept": "application/json", "X-API-KEY": apiKey },
            body: body?JSON.stringify(body):body,
            signal: AbortSignal.timeout(5000),
        });
        return response;     
    } catch (e) {
        console.log(e);
        return {status: 500};
    }
}

function updateMotorParameters(address, apiKey) {
    speed1 = Math.min(Math.max(-512.0*deltaTrans.x + 512.0*deltaTrans.y + 512.0*deltaRot, -512.0), 512.0);
    speed2 = Math.min(Math.max( 512.0*deltaTrans.x + 512.0*deltaTrans.y - 512.0*deltaRot, -512.0), 512.0);
    speed3 = Math.min(Math.max( 512.0*deltaTrans.x + 512.0*deltaTrans.y + 512.0*deltaRot, -512.0), 512.0);
    speed4 = Math.min(Math.max(-512.0*deltaTrans.x + 512.0*deltaTrans.y - 512.0*deltaRot, -512.0), 512.0);
    request(address, apiKey, "controller/0/motors/1", "POST", {enabled: true, name: "M1", values: [speed1], direction: "CCW"});
    request(address, apiKey, "controller/0/motors/2", "POST", {enabled: true, name: "M2", values: [speed2], direction: "CW"});
    request(address, apiKey, "controller/0/motors/3", "POST", {enabled: true, name: "M3", values: [speed3], direction: "CCW"});
    request(address, apiKey, "controller/0/motors/4", "POST", {enabled: true, name: "M4", values: [speed4], direction: "CW"});
    //renderRobotStatus(speed1, speed2, speed3, speed4);
}

function renderRobotStatus(speed1, speed2, speed3, speed4) {
    const ctx = robotStatusView.getContext("2d");
    ctx.resetTransform();
    ctx.translate(0.0, robotStatusView.clientHeight);
    ctx.scale(robotStatusView.clientWidth, -robotStatusView.clientHeight);
    ctx.translate(0.5, 0.5);
    ctx.clearRect(-robotStatusView.clientWidth/2.0, -robotStatusView.clientHeight/2.0, robotStatusView.clientWidth, robotStatusView.clientHeight);
    ctx.fillStyle = "red";
    ctx.fillRect(-0.125, -0.25, 0.25, 0.5);
    ctx.fillRect( 0.125,  0.15, 0.15, 0.2); // M1
    ctx.fillRect(-0.25,   0.15, 0.15, 0.2); // M2
    ctx.fillRect( 0.125, -0.35, 0.15, 0.2); // M3
    ctx.fillRect(-0.25,  -0.35, 0.15, 0.2); // M4
    ctx.beginPath();
    ctx.moveTo(0.0, 0.2);
    ctx.lineTo(0.1, 0.3);
    ctx.lineTo(-0.1, 0.3);
    ctx.lineTo(0.0, 0.2);
    ctx.fill();
    ctx.fillStyle = "black";
    ctx.font = "0.07px serif";
    ctx.textAlign = "center";
    ctx.scale(1.0, -1.0);
    ctx.fillText(speed1,  0.2,   -0.25, 0.18); // M1
    ctx.fillText(speed2, -0.175, -0.25, 0.18); // M2
    ctx.fillText(speed3,  0.2,    0.25, 0.18); // M3
    ctx.fillText(speed4, -0.175,  0.25, 0.18); // M4
}

/*function drawJoystick(canvas, mousePos) {
    const minSize = Math.min(canvas.clientWidth, canvas.clientHeight);
    const tmp = vSub(mousePos, {x: canvas.getBoundingClientRect().x+canvas.clientWidth/2.0, y: canvas.getBoundingClientRect().y+canvas.clientHeight/2.0});
    const len = Math.min(vLen(tmp), 0.35*minSize);
    const ang = vAng(tmp);
    const ctx = canvas.getContext("2d");
    ctx.resetTransform();
    ctx.translate(0.0, canvas.clientHeight);
    ctx.scale(1.0, -1.0);
    ctx.translate(canvas.clientWidth/2.0, canvas.clientHeight/2.0);
    ctx.clearRect(-canvas.clientWidth/2.0, -canvas.clientHeight/2.0, canvas.clientWidth, canvas.clientHeight);
    ctx.beginPath();
    ctx.arc(0.0, 0.0, 0.35*minSize, 0.0, 2.0 * Math.PI);
    ctx.fillStyle = "red";
    ctx.fill();
    ctx.beginPath();
    ctx.arc(len*Math.cos(ang), len*Math.sin(ang), 0.15*minSize, 0.0, 2.0 * Math.PI);
    ctx.fillStyle = "blue";
    ctx.fill();
}*/

function setupDesktopGUI(address, apiKey) {
    connectForm.remove();
    cameraView.hidden = false;
    //moveJoystick.hidden = false;
    //lookJoystick.hidden = false;
    //centerDot.style.display = "initial";
    document.addEventListener("keydown", async (e) => {
        if (pressedKeys.has(e.key)) {
            return;
        }
        if (e.key === "w" || e.key === "ArrowUp") {
            deltaTrans = {x: deltaTrans.x, y: 1.0};
        } else if (e.key === "a" || e.key === "ArrowLeft") {
            deltaTrans = {x: -1.0, y: deltaTrans.y};
        } else if (e.key === "s" || e.key === "ArrowDown") {
            deltaTrans = {x: deltaTrans.x, y: -1.0};
        } else if (e.key === "d" || e.key === "ArrowRight") {
            deltaTrans = {x: 1.0, y: deltaTrans.y};
        } else if (e.key === "e") {
            deltaRot = -1.0;
        } else if (e.key === "q") {
            deltaRot = 1.0;
        } else if (e.key === "Enter") {
            await request(address, apiKey, "controller/0/servomotors/1", "POST", {enabled: true, name: "S1", value: 512.0});
        } else if (e.key === " ") {
            await request(address, apiKey, "application/Meow/start", "POST");
        } 
        updateMotorParameters(address, apiKey);
        pressedKeys.add(e.key);
    });
    document.addEventListener("blur", async (e) => {
        pressedKeys.clear();
        deltaTrans = {x: 0.0, y: 0.0};
        deltaRot = 0.0;
        updateMotorParameters(address, apiKey);
        draggingScreen = false;
    });
    document.addEventListener("keyup", async (e) => {
        if (!pressedKeys.has(e.key)) {
            return;
        }
        pressedKeys.delete(e.key);
        if (e.key === "w" || e.key === "ArrowUp") {
            deltaTrans = {x: deltaTrans.x, y: 0.0};
        } else if (e.key === "a" || e.key === "ArrowLeft") {
            deltaTrans = {x: 0.0, y: deltaTrans.y};
        } else if (e.key === "s" || e.key === "ArrowDown") {
            deltaTrans = {x: deltaTrans.x, y: 0.0};
        } else if (e.key === "d" || e.key === "ArrowRight") {
            deltaTrans = {x: 0.0, y: deltaTrans.y};
        } else if (e.key === "e") {
            deltaRot = 0.0;
        } else if (e.key === "q") {
            deltaRot = 0.0;
        } else if (e.key === "Enter") {
            await request(address, apiKey, "controller/0/servomotors/1", "POST", {enabled: true, name: "S1", value: 210.0});
        }
        updateMotorParameters(address, apiKey);
    });
    /*document.addEventListener("mousedown", async (e) => {
        draggingScreen = true;
    });
    document.addEventListener("mousemove", async (e) => {
        if (draggingScreen) {
            deltaRot = 2.0*(e.clientX-window.screen.width/2)/window.screen.width;
            updateMotorParameters(address, apiKey);
        }
    });
    document.addEventListener("mouseup", async (e) => {
        draggingScreen = false;
    });*/
}

/*function setupMobileGUI(address, apiKey) {
    connectForm.remove();
    cameraView.hidden = false;
    moveJoystick.hidden = false;
    lookJoystick.hidden = false;
    drawJoystick(moveJoystick, {x: moveJoystick.getBoundingClientRect().x+moveJoystick.clientWidth/2.0, y: moveJoystick.getBoundingClientRect().y+moveJoystick.clientHeight/2.0});
    drawJoystick(lookJoystick, {x: lookJoystick.getBoundingClientRect().x+lookJoystick.clientWidth/2.0, y: lookJoystick.getBoundingClientRect().y+lookJoystick.clientHeight/2.0});
    document.addEventListener("blur", async (e) => {
        pressedKeys.clear();
        deltaTrans = {x: 0.0, y: 0.0};
        deltaRot = 0.0;
        updateMotorParameters(address, apiKey);
        draggingMoveJoystick = false;
        draggingLookJoystick = false;
    });
    lookJoystick.addEventListener("mousedown", async (e) => {
        drawJoystick(lookJoystick, {x: e.clientX, y: e.clientY});
        draggingLookJoystick = true;
    });
    moveJoystick.addEventListener("mousedown", async (e) => {
        drawJoystick(moveJoystick, {x: e.clientX, y: e.clientY});
        draggingMoveJoystick = true;
    });
    document.addEventListener("mousemove", async (e) => {
        if (draggingMoveJoystick) {
            drawJoystick(moveJoystick, {x: e.clientX, y: e.clientY});
            const minSize = Math.min(moveJoystick.clientWidth, moveJoystick.clientHeight);
            const tmp = vSub({x: e.clientX, y: e.clientY}, {x: moveJoystick.getBoundingClientRect().x+moveJoystick.clientWidth/2.0, y: moveJoystick.getBoundingClientRect().y+moveJoystick.clientHeight/2.0});
            const len = Math.min(vLen(tmp)/(0.35*minSize), 1.0);
            const ang = vAng(tmp);
            deltaTrans = {x: len*Math.cos(ang), y: len*Math.sin(ang)};
            updateMotorParameters(address, apiKey);
        }
        if (draggingLookJoystick) {
            drawJoystick(lookJoystick, {x: e.clientX, y: e.clientY});
            const tmp = vSub({x: e.clientX, y: e.clientY}, {x: lookJoystick.getBoundingClientRect().x+lookJoystick.clientWidth/2.0, y: lookJoystick.getBoundingClientRect().y+lookJoystick.clientHeight/2.0});
            const ang = vAng({x: -tmp.y, y: tmp.x});
            deltaRot = ang / Math.PI;
            updateMotorParameters(address, apiKey);
        }
    });
    document.addEventListener("mouseup", async (e) => {
        drawJoystick(moveJoystick, {x: moveJoystick.getBoundingClientRect().x+moveJoystick.clientWidth/2.0, y: moveJoystick.getBoundingClientRect().y+moveJoystick.clientHeight/2.0});
        drawJoystick(lookJoystick, {x: lookJoystick.getBoundingClientRect().x+lookJoystick.clientWidth/2.0, y: lookJoystick.getBoundingClientRect().y+lookJoystick.clientHeight/2.0});
        draggingMoveJoystick = false;
        draggingLookJoystick = false;
    });
}*/

async function connect() {
    const address = addressTextfield.value;
    const apiKey = apiKeyTextfield.value;
    addressTextfield.disabled = true;
    apiKeyTextfield.disabled = true;
    submitButton.disabled = true;
    statusLabel.innerText = "Connecting...";
    const response = await request(address, apiKey, "controller/0", "POST");
    if (response.status != 200) {
        addressTextfield.disabled = false;
        apiKeyTextfield.disabled = false;
        submitButton.disabled = false;
        statusLabel.innerText = "Connection failed!";
    } else {
        /*messageInput.hidden = false;
        messageSend.hidden = false;*/
        /*robotStatusView.hidden = false;
        renderRobotStatus(0, 0, 0, 0);*/
        /*if (matchMedia("(hover: none)").matches) {
            setupMobileGUI(address, apiKey);
        } else {*/
            setupDesktopGUI(address, apiKey);
        //}
        cameraReceiver.postMessage({address: address, apiKey: apiKey});
        cameraReceiver.onmessage = (e) => { cameraView.src = e.data; };
    }
}

/*async function sendMsg() {
    const address = addressTextfield.value;
    const apiKey = apiKeyTextfield.value;
    const msg = messageInput.value;
    try {
        await fetch("http://"+address+"/api/v1/workspaces/Chat/files", {
            method: "POST",
            //headers: { "Content-Type": "multipart/form-data; boundary=-----------------------------735323031399963166993862150", "X-API-KEY": apiKey},
            headers: { "Content-Type": "multipart/form-data; boundary=-----------------------------735323031399963166993862150", "X-API-KEY": apiKey},
            //body: "-----------------------------735323031399963166993862150\nContent-Disposition: form-data; name=\"label-content\"; filename=\"label-content.txt\"\nContent-Type: text/plain\n\n"+msg+"\n",
            body: "Content-Disposition: form-data; name=\"label-content\"; filename=\"label-content.txt\"\nContent-Type: text/plain\n\n"+msg+"\n",
            signal: AbortSignal.timeout(5000),
        });     
    } catch (e) {
        console.log(e);
    }
}*/