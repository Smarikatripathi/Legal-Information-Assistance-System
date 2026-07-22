import { motion } from "framer-motion";
import {
  UserPlus,
  MessageSquare,
  Search,
  CheckCircle,
} from "lucide-react";

const steps = [
  {
    icon: UserPlus,
    title: "Create Account",
    description:
      "Register and create your personal account to access legal assistance.",
    color: "#084FF4",
    bg: "#EFF6FF",
  },
  {
    icon: MessageSquare,
    title: "Ask Your Legal Question",
    description:
      "Explain your legal concern in simple language and start a conversation.",
    color: "#7C3AED",
    bg: "#F5F3FF",
  },
  {
    icon: Search,
    title: "AI Searches Legal Knowledge",
    description:
      "Our AI retrieves relevant legal information and analyzes your question.",
    color: "#059669",
    bg: "#ECFDF5",
  },
  {
    icon: CheckCircle,
    title: "Receive Easy-to-understand Answer",
    description:
      "Get clear explanations about laws, procedures, and possible actions.",
    color: "#C30A1C",
    bg: "#FEF2F2",
  },
];

const HowItWorks = () => {
  return (
    <section
      id="how-it-works"
      className="
        relative
        overflow-hidden
        bg-white
        py-24
      "
    >
      {/* Background Effects */}
      <div className="pointer-events-none absolute inset-0">

        <div
          className="
            absolute
            -top-40
            right-0
            h-96
            w-96
            rounded-full
            bg-[#084FF4]/10
            blur-3xl
          "
        />

        <div
          className="
            absolute
            -bottom-40
            left-0
            h-96
            w-96
            rounded-full
            bg-[#C30A1C]/10
            blur-3xl
          "
        />

      </div>


      <div className="landing-container relative">


        {/* Heading */}

        <motion.div
          initial={{
            opacity: 0,
            y: 30,
          }}
          whileInView={{
            opacity: 1,
            y: 0,
          }}
          viewport={{
            once: true,
          }}
          transition={{
            duration: 0.6,
          }}
          className="
            mx-auto
            mb-20
            max-w-3xl
            text-center
          "
        >

          <span
            className="
              rounded-full
              bg-[#084FF4]/10
              px-4
              py-2
              text-sm
              font-semibold
              text-[#084FF4]
            "
          >
            How It Works
          </span>


          <h2
            className="
              mt-5
              text-4xl
              font-bold
              text-slate-900
            "
          >
            From Question to
            <span className="text-[#C30A1C]">
              {" "}Legal Understanding
            </span>
          </h2>


          <p
            className="
              mt-5
              text-lg
              leading-8
              text-slate-600
            "
          >
            Our AI-powered system helps you understand legal information
            through a simple and guided process.
          </p>


        </motion.div>




        {/* Timeline */}

        <div
          className="
            relative
            mx-auto
            max-w-4xl
          "
        >


          {/* Timeline line */}

          <div
            className="
              absolute
              left-8
              top-8
              hidden
              h-[calc(100%-4rem)]
              w-[2px]
              bg-slate-200
              md:block
            "
          />



          <div
            className="
              space-y-10
            "
          >

            {steps.map((step,index)=>{

              const Icon = step.icon;


              return (

                <motion.div
                  key={step.title}

                  initial={{
                    opacity:0,
                    x:-40,
                  }}

                  whileInView={{
                    opacity:1,
                    x:0,
                  }}

                  viewport={{
                    once:true,
                  }}

                  transition={{
                    duration:0.5,
                    delay:index*0.15,
                  }}

                  className="
                    relative
                    flex
                    items-start
                    gap-8
                  "
                >


                  {/* Icon */}

                  <div
                    className="
                      relative
                      z-10
                      flex
                      h-16
                      w-16
                      shrink-0
                      items-center
                      justify-center
                      rounded-full
                      shadow-md
                    "

                    style={{
                      backgroundColor:step.bg,
                      border:`3px solid ${step.color}`,
                    }}
                  >

                    <Icon
                      size={28}
                      style={{
                        color:step.color,
                      }}
                    />

                  </div>




                  {/* Content */}

                  <div
                    className="
                      flex-1
                      rounded-3xl
                      border
                      border-slate-200
                      bg-white
                      p-6
                      shadow-sm
                      transition-all
                      duration-300
                      hover:-translate-y-1
                      hover:shadow-xl
                    "
                  >

                    <div
                      className="
                        text-sm
                        font-bold
                      "

                      style={{
                        color:step.color,
                      }}
                    >
                      STEP {index + 1}
                    </div>


                    <h3
                      className="
                        mt-2
                        text-xl
                        font-bold
                        text-slate-900
                      "
                    >
                      {step.title}
                    </h3>


                    <p
                      className="
                        mt-3
                        leading-7
                        text-slate-600
                      "
                    >
                      {step.description}
                    </p>


                  </div>


                </motion.div>

              );

            })}


          </div>


        </div>


      </div>


    </section>
  );
};

export default HowItWorks;