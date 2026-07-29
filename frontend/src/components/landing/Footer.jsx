import { Scale, Mail, Phone } from "lucide-react";
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="bg-slate-950 text-white">

      <div className="landing-container py-10 sm:py-12">

        <div className="
          grid 
          gap-8
          sm:grid-cols-2
          lg:grid-cols-4
        ">

          {/* Brand */}
          <div className="sm:col-span-2">

            <div className="flex items-center gap-3">

              <div
                className="
                  flex
                  h-10
                  w-10
                  shrink-0
                  items-center
                  justify-center
                  rounded-xl
                  bg-[#C30A1C]
                "
              >
                <Scale size={22} />
              </div>

              <h3 className="
                text-lg
                font-bold
                leading-tight
              ">
                Legal Information
                <br />
                Assistance System
              </h3>

            </div>


            <p className="
              mt-4
              max-w-md
              text-sm
              leading-6
              text-slate-400
            ">
              An AI-powered platform that helps users understand
              legal information through simple explanations,
              intelligent assistance, and accessible resources.
            </p>

          </div>



          {/* Navigation */}
          <div>

            <h4 className="mb-4 font-semibold">
              Navigation
            </h4>

            <ul className="space-y-2.5 text-sm text-slate-400">

              <li>
                <a href="#home" className="hover:text-white transition">
                  Home
                </a>
              </li>

              <li>
                <a href="#features" className="hover:text-white transition">
                  Features
                </a>
              </li>

              <li>
                <a href="#how-it-works" className="hover:text-white transition">
                  How It Works
                </a>
              </li>

            </ul>

          </div>



          {/* Contact */}
          <div>

            <h4 className="mb-4 font-semibold">
              Contact
            </h4>

            <ul className="space-y-3 text-sm text-slate-400">

              <li>
                <Link
                  to="/login"
                  className="hover:text-white transition"
                >
                  Login
                </Link>
              </li>

              <li>
                <Link
                  to="/signup"
                  className="hover:text-white transition"
                >
                  Get Started
                </Link>
              </li>


              <li className="flex items-center gap-3 pt-1">
                <Mail
                  size={15}
                  className="text-[#084FF4]"
                />
                <span>
                  smritipokhrel061@gmail.com
                </span>
              </li>


              <li className="flex items-center gap-3">
                <Phone
                  size={15}
                  className="text-[#C30A1C]"
                />
                <span>
                  +977 9812345678
                </span>
              </li>


            </ul>

          </div>


        </div>



        <div
          className="
            mt-8
            border-t
            border-slate-800
            pt-5
            text-center
            text-xs
            text-slate-500
          "
        >
          © {new Date().getFullYear()} Legal Information Assistance System.
          All rights reserved.
        </div>


      </div>

    </footer>
  );
};

export default Footer;