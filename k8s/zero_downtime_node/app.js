const express = require('express');
const app = express();
const port = 3000;

// --------------------------------------------------- //
// DO NOT MODIFY THE BELOW CODE SNIPPET

// This variable indicates server readiness
let ready = false;
// --------------------------------------------------- //

app.get('/', (req, res) => {
  let x = 0.0001;
  for (let i = 0; i <= 1000000; i++) {
    x += Math.sqrt(x);
  }
  res.send('OK ');
});


app.get('/ready', (req, res) => {
  // TODO return status code 200 if server is ready (indicated by the `ready` variable), otherwise 503.
  res.send(200);
});

app.get('/health', (req, res) => {
  res.send(200);
});

// This handler is called whenever k8s sends a SIGTERM to the container, before terminating the Pod
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server')

  // TODO indicate that the server is not ready, and wait for k8s to stop routing traffic before closing the server.
  server.close(() => {
    console.log('HTTP server closed')
  })
})


// This function call sets the `ready` variable to be `true` after 20 seconds of server running
setTimeout(() => {
  app.listen(port, '0.0.0.0', () => {
    console.log("Server running");
    ready = true;
  });
}, 20000);


