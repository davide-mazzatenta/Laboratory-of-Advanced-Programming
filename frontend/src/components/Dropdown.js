// components/Dropdown.js
import React, { useState, useRef, useEffect } from "react";

export default function Dropdown({ label = "Menu", options = [], onSelect }) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);

  // close menu if click outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative inline-block" ref={menuRef}>
      {/* Button */}
      <button
        onClick={() => setOpen(!open)}
        className="px-3 py-1 border rounded bg-white shadow hover:bg-gray-100"
      >
        {label} ▾
      </button>

      {/* Menu */}
      {open && (
        <div className="absolute right-0 mt-1 w-48 bg-white border rounded shadow-lg z-50">
          {options.map((opt, i) => (
            <div
              key={i}
              onClick={() => {
                onSelect(opt.value);
                setOpen(false);
              }}
              className="px-3 py-2 cursor-pointer hover:bg-gray-200"
            >
              {opt.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}