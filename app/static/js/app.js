// app/static/js/app.js
let uploadBtn = document.getElementById("uploadBtn");
let fileInput = document.getElementById("file");
let uploadStatus = document.getElementById("uploadStatus");
uploadBtn.onclick = async () => {
  if(!fileInput.files.length) return alert("Select a file");
  let f = fileInput.files[0];
  let fd = new FormData();
  fd.append("file", f);
  uploadStatus.innerText = "Uploading...";
  let res = await fetch("/upload", {method:"POST", body: fd});
  let j = await res.json();
  uploadStatus.innerText = "Uploaded: " + j.filename;
};

let askBtn = document.getElementById("askBtn");
askBtn.onclick = async () => {
  let q = document.getElementById("question").value;
  let wantAudio = document.getElementById("wantAudio").checked;
  let wantChart = document.getElementById("wantChart").checked;
  if(!q) return alert("Type a question");
  let fd = new FormData();
  fd.append("question", q);
  fd.append("want_audio", wantAudio);
  fd.append("want_chart", wantChart);
  let res = await fetch("/ask", {method:"POST", body: fd});
  let j = await res.json();
  document.getElementById("answer").innerText = j.answer || "";
  if(j.chart){
    let img = document.getElementById("chartImg");
    img.src = j.chart;
    img.style.display = "block";
  }
  if(j.audio){
    let player = document.getElementById("player");
    player.src = j.audio;
    player.style.display = "block";
    player.play();
  }
};

// simple recording for /stt
let recBtn = document.getElementById("recBtn");
let recStatus = document.getElementById("recStatus");
let mediaRecorder, chunks = [];
recBtn.onclick = async () => {
  if(!mediaRecorder || mediaRecorder.state === "inactive"){
    let stream = await navigator.mediaDevices.getUserMedia({audio:true});
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = async () => {
      let blob = new Blob(chunks, {type: 'audio/webm'});
      chunks = [];
      let fd = new FormData();
      fd.append("file", blob, "query.webm");
      recStatus.innerText = "Uploading audio for transcription...";
      let res = await fetch("/stt", {method:"POST", body: fd});
      let j = await res.json();
      recStatus.innerText = "Transcribed: " + j.text;
      document.getElementById("question").value = j.text;
    };
    mediaRecorder.start();
    recStatus.innerText = "Recording... click again to stop.";
  } else {
    mediaRecorder.stop();
    recStatus.innerText = "Processing audio...";
  }
};