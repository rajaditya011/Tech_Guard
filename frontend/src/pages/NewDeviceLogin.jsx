import React, { useState, useRef, useEffect } from "react";
import { Eye, EyeOff, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import AppShell from "../components/layout/AppShell";
import { cn } from "../lib/utils";

const Button = React.forwardRef(({ className, variant = "default", size = "default", ...props }, ref) => {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50",
        size === "default" && "h-10 px-4 py-2",
        size === "sm" && "h-9 px-3",
        size === "lg" && "h-11 px-8",
        className
      )}
      ref={ref}
      {...props}
    />
  );
});
Button.displayName = "Button";

const Input = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <input
      className={cn(
        "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  );
});
Input.displayName = "Input";

const DotMap = () => {
  const canvasRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  const routes = [
    { start: { x: 100, y: 150, delay: 0 }, end: { x: 200, y: 80, delay: 2 }, color: "#3b82f6" },
    { start: { x: 200, y: 80, delay: 2 }, end: { x: 260, y: 120, delay: 4 }, color: "#3b82f6" },
    { start: { x: 50, y: 50, delay: 1 }, end: { x: 150, y: 180, delay: 3 }, color: "#3b82f6" },
    { start: { x: 280, y: 60, delay: 0.5 }, end: { x: 180, y: 180, delay: 2.5 }, color: "#3b82f6" },
  ];

  const generateDots = (width, height) => {
    const dots = [];
    const gap = 12;
    for (let x = 0; x < width; x += gap) {
      for (let y = 0; y < height; y += gap) {
        const isInMapShape =
          ((x < width * 0.25 && x > width * 0.05) && (y < height * 0.4 && y > height * 0.1)) ||
          ((x < width * 0.25 && x > width * 0.15) && (y < height * 0.8 && y > height * 0.4)) ||
          ((x < width * 0.45 && x > width * 0.3) && (y < height * 0.35 && y > height * 0.15)) ||
          ((x < width * 0.5 && x > width * 0.35) && (y < height * 0.65 && y > height * 0.35)) ||
          ((x < width * 0.7 && x > width * 0.45) && (y < height * 0.5 && y > height * 0.1)) ||
          ((x < width * 0.8 && x > width * 0.65) && (y < height * 0.8 && y > height * 0.6));

        if (isInMapShape && Math.random() > 0.3) {
          dots.push({ x, y, radius: 1, opacity: Math.random() * 0.5 + 0.1 });
        }
      }
    }
    return dots;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resizeObserver = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width, height });
      canvas.width = width;
      canvas.height = height;
    });

    resizeObserver.observe(canvas.parentElement);
    return () => resizeObserver.disconnect();
  }, []);

  useEffect(() => {
    if (!dimensions.width || !dimensions.height) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dots = generateDots(dimensions.width, dimensions.height);
    let animationFrameId;
    let startTime = Date.now();

    function drawDots() {
      ctx.clearRect(0, 0, dimensions.width, dimensions.height);
      dots.forEach(dot => {
        ctx.beginPath();
        ctx.arc(dot.x, dot.y, dot.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${dot.opacity})`;
        ctx.fill();
      });
    }

    function drawRoutes() {
      const currentTime = (Date.now() - startTime) / 1000;
      routes.forEach(route => {
        const elapsed = currentTime - route.start.delay;
        if (elapsed <= 0) return;
        const progress = Math.min(elapsed / 3, 1);
        const x = route.start.x + (route.end.x - route.start.x) * progress;
        const y = route.start.y + (route.end.y - route.start.y) * progress;
        
        ctx.beginPath();
        ctx.moveTo(route.start.x, route.start.y);
        ctx.lineTo(x, y);
        ctx.strokeStyle = route.color;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        
        ctx.beginPath();
        ctx.arc(route.start.x, route.start.y, 3, 0, Math.PI * 2);
        ctx.fillStyle = route.color;
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fillStyle = "#60a5fa";
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(96, 165, 250, 0.3)";
        ctx.fill();
        
        if (progress === 1) {
          ctx.beginPath();
          ctx.arc(route.end.x, route.end.y, 3, 0, Math.PI * 2);
          ctx.fillStyle = route.color;
          ctx.fill();
        }
      });
    }
    
    function animate() {
      drawDots();
      drawRoutes();
      const currentTime = (Date.now() - startTime) / 1000;
      if (currentTime > 15) startTime = Date.now();
      animationFrameId = requestAnimationFrame(animate);
    }
    animate();
    return () => cancelAnimationFrame(animationFrameId);
  }, [dimensions]);

  return (
    <div className="relative w-full h-full overflow-hidden">
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
    </div>
  );
};

export default function NewDeviceLogin() {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        await register(email, password, 'new_device');
      } else {
        await login(email, password);
      }
      navigate('/new-device/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <AppShell>
      <div className="flex w-full min-h-screen py-10 items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-5xl overflow-hidden rounded-2xl flex bg-[#090b13] text-white shadow-2xl border border-[#1f2130]"
        >
          {/* Left side - Map */}
          <div className="hidden md:block w-1/2 h-[600px] relative overflow-hidden border-r border-[#1f2130]">
            <div className="absolute inset-0 bg-gradient-to-br from-[#0f1120] to-[#151929]">
              <DotMap />
              
              <div className="absolute inset-0 flex flex-col items-center justify-center p-8 z-10 bg-[#060818]/60 backdrop-blur-[2px]">
                <motion.div 
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6, duration: 0.5 }}
                  className="mb-6"
                >
                  <div className="h-14 w-14 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center glow-blue">
                    <ArrowRight className="text-white h-7 w-7" />
                  </div>
                </motion.div>
                <motion.h2 
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7, duration: 0.5 }}
                  className="text-4xl font-extrabold mb-3 text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500 leading-tight"
                >
                  HomeGuardian AI
                </motion.h2>
                <motion.p 
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8, duration: 0.5 }}
                  className="text-sm text-center text-gray-300 max-w-[280px]"
                >
                  Understanding behavior, not just detecting movement. Secure your global dashboard.
                </motion.p>
              </div>
            </div>
          </div>
          
          {/* Right side - Sign In Form */}
          <div className="w-full md:w-1/2 px-8 py-10 md:p-12 flex flex-col justify-center bg-[#0d1023]">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="inline-block px-3 py-1 mb-4 rounded-full text-xs font-mono uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Owner Dashboard
              </div>
              <h1 className="text-3xl font-bold mb-2">{isRegister ? 'Create Account' : 'Welcome back'}</h1>
              <p className="text-gray-400 mb-8">{isRegister ? 'Set up your master dashboard' : 'Sign in to your global network'}</p>
              
              <form className="space-y-5" onSubmit={handleSubmit}>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-1.5">
                    Email or Username <span className="text-blue-500">*</span>
                  </label>
                  <Input
                    id="email"
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="admin@homeguardian.ai"
                    required
                    className="bg-[#13151f] border-[#2a2d3a] placeholder:text-gray-600 text-gray-200 w-full focus:border-blue-500 transition-colors"
                  />
                </div>
                
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-1.5">
                    Password <span className="text-blue-500">*</span>
                  </label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={isPasswordVisible ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Minimum 6 characters"
                      required minLength={6}
                      className="bg-[#13151f] border-[#2a2d3a] placeholder:text-gray-600 text-gray-200 w-full pr-10 focus:border-blue-500 transition-colors"
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 hover:text-gray-300 transition-colors cursor-pointer"
                      onClick={() => setIsPasswordVisible(!isPasswordVisible)}
                    >
                      {isPasswordVisible ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400">
                    {error}
                  </div>
                )}
                
                <motion.div 
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.98 }}
                  onHoverStart={() => setIsHovered(true)}
                  onHoverEnd={() => setIsHovered(false)}
                  className="pt-4"
                >
                  <Button
                    type="submit"
                    disabled={loading}
                    className={cn(
                      "w-full bg-gradient-to-r relative overflow-hidden from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white py-6 text-base font-semibold rounded-lg transition-all duration-300 border-0",
                      isHovered ? "shadow-lg shadow-blue-500/25" : "",
                      loading && "opacity-70"
                    )}
                  >
                    <span className="flex items-center justify-center">
                      {loading ? 'Authenticating...' : (isRegister ? 'Create Master Account' : 'Access Dashboard')}
                      {!loading && <ArrowRight className="ml-2 h-4 w-4" />}
                    </span>
                    {isHovered && !loading && (
                      <motion.span
                        initial={{ left: "-100%" }}
                        animate={{ left: "100%" }}
                        transition={{ duration: 1, ease: "easeInOut" }}
                        className="absolute top-0 bottom-0 left-0 w-20 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                        style={{ filter: "blur(8px)" }}
                      />
                    )}
                  </Button>
                </motion.div>
                
                <div className="text-center mt-6 pt-4 border-t border-[#1f2130] flex flex-col gap-3">
                  <button type="button" onClick={() => setIsRegister(!isRegister)} className="text-gray-400 hover:text-blue-400 text-sm transition-colors bg-transparent border-none cursor-pointer">
                    {isRegister ? 'Already an admin? Sign in' : "Don't have an account? Sign up"}
                  </button>
                  <Link to="/old-device/login" className="text-gray-500 hover:text-gray-300 text-xs transition-colors">
                    Connecting an old camera node? Connect here
                  </Link>
                </div>
              </form>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </AppShell>
  );
}
