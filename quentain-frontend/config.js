const isProd = process.env.NODE_ENV === 'production'

export default {
  serverPath: isProd ? "https://quentain-server.onrender.com": "http://localhost:5050",
}
