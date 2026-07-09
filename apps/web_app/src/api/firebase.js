import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyBzNVOk4JfavmlMPCSC8dECpjiFT1bLB6c",
  authDomain: "lexai-3fd1a.firebaseapp.com",
  projectId: "lexai-3fd1a",
  storageBucket: "lexai-3fd1a.firebasestorage.app",
  messagingSenderId: "589308663044",
  appId: "1:589308663044:web:3d249d121be011d430ac51",
  measurementId: "G-7WWFYDHPZG"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);
export default app;
