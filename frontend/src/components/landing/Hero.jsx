import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import heroImage from "../../assets/hero-legal-assistance.png";

const Hero = () => {
  return (
    <section
      id="home"
      className="relative min-h-screen scroll-mt-24 overflow-hidden bg-white pt-10"
    >
      {/* Background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 -right-32 h-96 w-96 rounded-full bg-[#084FF4]/10 blur-3xl" />
        <div className="absolute -bottom-32 -left-32 h-96 w-96 rounded-full bg-[#C30A1C]/10 blur-3xl" />
      </div>
      <div className="landing-container relative flex py-24 lg:min-h-[85vh] flex-col items-center justify-center gap-16 lg:flex-row">
        {/* Left */}
        <motion.div
          initial={{ opacity: 0, y: 35 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="flex-1 text-center lg:text-left"
        >
          <span className="inline-flex rounded-full bg-[#084FF4]/10 px-4 py-2 text-sm font-semibold text-[#084FF4]">
            AI-Powered Legal Assistance
          </span>

          <h1 className="mt-6 text-5xl font-bold leading-tight text-black lg:text-6xl">
            Legal Information
            <br />
            Made Simple & Accessible
          </h1>

          <p className="mx-auto mt-7 max-w-xl text-lg leading-8 text-slate-600 lg:mx-0">
            Understand your legal rights with confidence. Get clear, AI-assisted
            explanations of laws, legal procedures, and important legal
            information through a modern and easy-to-use platform.
          </p>

          {/* CTA */}
          <div className="mt-10">
            <Link
              to="/signup"
              className="inline-flex items-center gap-2 rounded-xl bg-[#C30A1C] px-8 py-4 text-lg font-semibold text-white transition-all duration-300 hover:bg-[#A10818] hover:shadow-xl hover:shadow-[#C30A1C]/25 active:scale-95"
            >
              Get Started
              <ArrowRight size={20} />
            </Link>
          </div>
        </motion.div>

        {/* Right */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.7 }}
          className="flex flex-1 justify-center"
        >
          <div className="relative w-full max-w-xl">
            <div className="absolute -inset-6 rounded-full bg-linear-to-br from-[#084FF4]/20 to-[#C30A1C]/20 blur-3xl" />

            <img
              src={heroImage}
              alt="Legal Information Assistance System"
              className="relative w-full"
            />
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
