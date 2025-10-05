"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import LoginModal from "@/components/LoginModal";

export default function Home() {
  const router = useRouter();

  // Check if user is already authenticated and redirect to dashboard
  useEffect(() => {
    const authStatus = sessionStorage.getItem("bharatace_authenticated");
    const token = sessionStorage.getItem("admin_token");
    
    if (authStatus === "true" && token) {
      router.push("/dashboard");
    }
  }, [router]);

  const handleLogin = () => {
    router.push("/dashboard");
  };

  return (
    <>
      {/* Login Modal */}
      <LoginModal onLogin={handleLogin} />
    </>
  );
}
