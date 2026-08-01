const http = require("node:http");

const port = Number(process.env.PORT || 3000);
const appEnv = process.env.APP_ENV || "local";
const releaseVersion = process.env.RELEASE_VERSION || "dev";
const featureFlagSample = process.env.FEATURE_FLAG_SAMPLE === "true";
const hasSecretCheckValue = Boolean(process.env.SECRET_CHECK_VALUE);

function sendJson(res, statusCode, body) {
  const payload = JSON.stringify(body, null, 2);
  res.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store"
  });
  res.end(payload + "\n");
}

function logRequest(req, statusCode) {
  const now = new Date().toISOString();
  console.log(`${now} ${req.method} ${req.url} ${statusCode}`);
}

const server = http.createServer((req, res) => {
  if (req.url === "/") {
    const statusCode = 200;
    sendJson(res, statusCode, {
      service: "openship-staging-health",
      message: "OpenShip staging sample is running.",
      appEnv,
      releaseVersion
    });
    logRequest(req, statusCode);
    return;
  }

  if (req.url === "/health") {
    const statusCode = 200;
    sendJson(res, statusCode, {
      status: "ok",
      checkedAt: new Date().toISOString(),
      appEnv,
      releaseVersion
    });
    logRequest(req, statusCode);
    return;
  }

  if (req.url === "/config-check") {
    const statusCode = 200;
    sendJson(res, statusCode, {
      appEnv,
      releaseVersion,
      featureFlagSample,
      hasSecretCheckValue
    });
    logRequest(req, statusCode);
    return;
  }

  const statusCode = 404;
  sendJson(res, statusCode, {
    error: "not_found",
    path: req.url
  });
  logRequest(req, statusCode);
});

server.listen(port, () => {
  console.log(`openship-staging-health listening on ${port}`);
});
