export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const APP_CONFIG = {
  name: "Santé+",
  version: "3.0.0",
  apiBase: API_URL,
  bitcoinTestnet: import.meta.env.VITE_BITCOIN_TESTNET === "true" || import.meta.env.DEV,
};

export const DEMO_CREDENTIALS = {
  patient: {
    email: "bienvenuesegnon@gmail.com",
    password: "123456",
  },
  hospitalAdmin: {
    email: "hopital_cotonou@hopital.bj",
    password: "pass123",
  },
};
