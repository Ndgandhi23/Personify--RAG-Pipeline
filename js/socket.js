const socket = new WebSocket("ws://127.0.0.1:8000");

socket.onopen = function (event) {
  console.log("Connected to the WebSocket server.");
};

socket.onmessage = function (event) {
  console.log("Data received from server:", event.data);
  refreshApplicationGrid(event.data);
};

socket.addEventListener("application_processed", function (event) {
  console.log("Application processed event received:", event.detail);
  applicationProcessed(event.detail);
});

function applicationProcessed(applicationInfo){
  //If there is an application in .application-grid .apps existing with the class
  //{company}-{role}, update
  //Else, just create a new application element with application info
}
