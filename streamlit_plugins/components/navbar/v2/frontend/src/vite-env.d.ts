/// <reference types="vite/client" />

declare namespace React {
  interface InputHTMLAttributes<T> {
    // Non-standard attribute for directory uploads
    webkitdirectory?: string;
  }
}
