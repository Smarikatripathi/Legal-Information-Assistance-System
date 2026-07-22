import { motion } from "framer-motion";
import {
  Bot,
  BookOpenText,
  ShieldCheck,
  Search,
} from "lucide-react";

const features = [
  {
    icon: Bot,
    title: "AI Legal Assistant",
    short:
      "Ask legal questions and receive clear AI-powered guidance.",
    description:
      "Ask legal questions in natural language and receive clear, easy-to-understand answers based on Nepal's legal information.",
    color: "#7C3AED",
  },
  {
    icon: BookOpenText,
    title: "Legal Knowledge Base",
    short:
      "Access important legal information in one place.",
    description:
      "Access legal acts, regulations, and legal concepts in one centralized platform without searching multiple websites.",
    color: "#084FF4",
  },
  {
    icon: Search,
    title: "Smart Legal Search",
    short:
      "Find relevant legal information quickly using AI.",
    description:
      "Quickly find relevant legal information using intelligent search powered by AI retrieval techniques.",
    color: "#0891B2",
  },
  {
    icon: ShieldCheck,
    title: "Secure & Reliable",
    short:
      "Your information stays private and protected.",
    description:
      "Your conversations remain private while the platform delivers trustworthy legal information whenever you need it.",
    color: "#059669",
  },
];

const Features = () => {
  return (
    <section
      id="features"
      className="
        relative
        overflow-hidden
        scroll-mt-24
        bg-slate-50
        py-20
      "
    >

      {/* Background accents */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 -left-32 h-96 w-96 rounded-full bg-[#084FF4]/10 blur-3xl" />

        <div className="absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-[#C30A1C]/10 blur-3xl" />
      </div>


      <div className="landing-container relative">

        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mx-auto mb-16 max-w-3xl text-center"
        >
          <span className="
            inline-flex
            rounded-full
            bg-[#084FF4]/10
            px-4
            py-2
            text-sm
            font-semibold
            text-[#084FF4]
          ">
            Features
          </span>


          <h2 className="mt-5 text-4xl font-bold text-slate-900">
            Everything You Need to
            <span className="text-[#084FF4]"> Understand </span>
            Legal Information
          </h2>


          <p className="
            mt-5
            text-lg
            leading-8
            text-slate-600
          ">
            A modern platform combining artificial intelligence
            with legal information to make understanding laws easier.
          </p>

        </motion.div>



        {/* Cards */}
        <div className="
          grid
          gap-8
          md:grid-cols-2
          xl:grid-cols-4
        ">

          {features.map((feature, index) => {

            const Icon = feature.icon;

            return (
              <motion.div
                key={feature.title}

                initial={{
                  opacity: 0,
                  y: 35,
                }}

                whileInView={{
                  opacity: 1,
                  y: 0,
                }}

                viewport={{
                  once: true,
                }}

                transition={{
                  duration: 0.5,
                  delay: index * 0.1,
                }}

                whileHover={{
                  y: -10,
                }}

                className="
                  group
                  rounded-3xl
                  border
                  border-slate-200
                  bg-white
                  p-8
                  shadow-sm
                  transition-all
                  duration-300
                  hover:shadow-2xl
                "
              >

                {/* Icon */}
                <div
                  className="
                    flex
                    h-16
                    w-16
                    items-center
                    justify-center
                    rounded-2xl
                  "

                  style={{
                    backgroundColor: `${feature.color}15`,
                  }}
                >

                  <Icon
                    size={30}
                    style={{
                      color: feature.color,
                    }}
                  />

                </div>



                <h3 className="
                  mt-6
                  text-xl
                  font-bold
                  text-slate-900
                ">
                  {feature.title}
                </h3>



                {/* Short text */}
                <p className="
                  mt-4
                  leading-7
                  text-slate-600
                  transition-all
                  duration-300
                  group-hover:hidden
                ">
                  {feature.short}
                </p>



                {/* Full description */}
                <p className="
                  mt-4
                  hidden
                  leading-7
                  text-slate-600
                  group-hover:block
                  animate-fade-in
                ">
                  {feature.description}
                </p>



                {/* Accent line */}
                <div
                  className="
                    mt-8
                    h-1
                    w-12
                    rounded-full
                    transition-all
                    duration-300
                    group-hover:w-20
                  "

                  style={{
                    backgroundColor: feature.color,
                  }}
                />

              </motion.div>
            );
          })}

        </div>

      </div>

    </section>
  );
};

export default Features;