# OKX Webhook Relay

A lightweight Flask webhook that receives payloads from Google Sheets, generates OKX-compatible HMAC-SHA256 signatures, and returns them in Base64 format.

## 🔧 Features
- Accepts POST requests with `payload` and `secret`
- Returns signed payload for OKX REST API v5
- Logs incoming requests for inspection
- Compatible with local testing and Render deployment

## 🚀 How to Run Locally
```bash
python okx_signer.py