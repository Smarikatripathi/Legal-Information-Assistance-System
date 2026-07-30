import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Menu, X, Scale } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const Navbar = () => {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll);

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navItems = [
    { label: "Home", href: "#home" },
    { label: "Features", href: "#features" },
    { label: "How It Works", href: "#how-it-works" },
 
  ];

  return (
    <header
      className={`fixed top-0 left-0 z-50 w-full transition-all duration-300 ${
        scrolled
          ? "border-b border-slate-200 bg-white/90 backdrop-blur-xl shadow-sm"
          : "bg-white/70 backdrop-blur-lg"
      }`}
    >
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#2563EB]">
            <Scale className="h-6 w-6 text-white" />
          </div>

          <div className="hidden sm:block leading-tight">
            <h1 className="text-sm font-bold text-[#084FF4]">
              Legal Information
            </h1>

            <p className="text-xs text-slate-500">Assistance System</p>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden items-center gap-2 lg:flex">
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="
                rounded-xl
                px-4
                py-2
                font-medium
                text-slate-700
                transition-all
                duration-200
                hover:bg-blue-50
                hover:text-[#084FF4]
              "
            >
              {item.label}
            </a>
          ))}
        </nav>

        {/* Desktop Buttons */}
        <div className="hidden items-center gap-3 lg:flex">
          <Link
            to="/login"
            className="
    rounded-xl
    bg-[#084FF4]
    px-5
    py-2.5
    font-medium
    text-white
    transition-all
    duration-300
    hover:bg-[#063fd1]
    hover:shadow-lg
    hover:shadow-[#084FF4]/30
    active:scale-95
  "
          >
            Login
          </Link>

          <Link
            to="/signup"
            className="
              rounded-xl
              bg-[#2563EB]
              px-5
              py-2.5
              font-medium
              text-white
              transition-all
              duration-200
              hover:bg-primary-hover
            "
          >
            Get Started
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setOpen(!open)}
          className="rounded-lg p-2 transition hover:bg-slate-100 lg:hidden"
        >
          {open ? (
            <X className="h-7 w-7 text-slate-700" />
          ) : (
            <Menu className="h-7 w-7 text-slate-700" />
          )}
        </button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.2 }}
            className="border-t border-slate-200 bg-white shadow-lg lg:hidden"
          >
            <div className="flex flex-col gap-2 px-6 py-6">
              {navItems.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className="
                    rounded-xl
                    px-4
                    py-3
                    font-medium
                    text-slate-700
                    transition-all
                    duration-200
                    hover:bg-blue-50
                    hover:text-[#084FF4]
                  "
                >
                  {item.label}
                </a>
              ))}

              <div className="mt-4 flex flex-col gap-3">
                <Link
                  to="/login"
                  onClick={() => setOpen(false)}
                  className="
    rounded-xl
    bg-[#084FF4]
    py-3
    text-center
    font-semibold
    text-white
    transition-all
    duration-300
    hover:bg-[#063fd1]
    hover:shadow-lg
    hover:shadow-[#084FF4]/30
    active:scale-95
  "
                >
                  Login
                </Link>

                <Link
                  to="/signup"
                  onClick={() => setOpen(false)}
                  className="
                    rounded-xl
                    bg-[#2563EB]
                    py-3
                    text-center
                    font-semibold
                    text-white
                    transition-all
                    duration-200
                    hover:bg-primary-hover
                  "
                >
                  Get Started
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

export default Navbar;
