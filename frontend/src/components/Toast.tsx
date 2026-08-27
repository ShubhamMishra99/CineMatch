import React, { useEffect } from "react";
import { CheckCircle } from "lucide-react";

interface ToastProps {
  message: string;
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="toast-message">
      <CheckCircle size={16} style={{ color: "var(--match-green)" }} />
      <span>{message}</span>
    </div>
  );
};
