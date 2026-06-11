import { spawn } from "child_process";
import path from "path";

export const runPythonPrediction = (payload) =>
  new Promise((resolve, reject) => {
    const scriptPath = path.join(process.cwd(), "ml", "predict.py");
    const pythonProcess = spawn(process.env.PYTHON_BIN || "python", [scriptPath], {
      env: process.env,
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    pythonProcess.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        return reject(new Error(`Python prediction failed: ${stderr || "Unknown error"}`));
      }

      try {
        const parsed = JSON.parse(stdout.trim());
        return resolve(parsed);
      } catch {
        return reject(new Error(`Invalid prediction response: ${stdout}`));
      }
    });

    pythonProcess.stdin.write(JSON.stringify(payload));
    pythonProcess.stdin.end();
  });
