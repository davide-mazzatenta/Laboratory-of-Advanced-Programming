//components/Animation.js
import React, { useState, useEffect } from 'react';

// Enhanced typing effect with longer durations and smoother transitions
export const TypingEffect = ({
  messages,
  typingSpeed = 30,
  deleteSpeed = 15,
  delayAfterType = 5000,
}) => {
  const [displayText, setDisplayText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isWaiting, setIsWaiting] = useState(false);

  useEffect(() => {
    const currentMessage = messages[currentIndex];

    if (isWaiting) {
      const waitTimer = setTimeout(() => {
        setIsWaiting(false);
        setIsDeleting(true);
      }, delayAfterType);
      return () => clearTimeout(waitTimer);
    }

    if (isDeleting && displayText === '') {
      setIsDeleting(false);
      setCurrentIndex((currentIndex + 1) % messages.length);
      return;
    }

    if (!isDeleting && displayText === currentMessage) {
      setIsWaiting(true);
      return;
    }

    const timeout = setTimeout(
      () => {
        if (isDeleting) {
          setDisplayText((prev) => prev.substring(0, prev.length - 1));
        } else {
          setDisplayText(currentMessage.substring(0, displayText.length + 1));
        }
      },
      isDeleting ? deleteSpeed : typingSpeed,
    );

    return () => clearTimeout(timeout);
  }, [
    displayText,
    isDeleting,
    currentIndex,
    messages,
    typingSpeed,
    deleteSpeed,
    delayAfterType,
    isWaiting,
  ]);

  return <span>{displayText}</span>;
};
