const Button = ({
  children,
  variant = "primary",
  size = "md",
  type = "button",
  className = "",
  ...props
}) => {

  const variants = {
    primary:
      "bg-[#084FF4] text-white hover:bg-[#063fd1]",

    danger:
      "bg-[#C30A1C] text-white hover:bg-[#a70917]",

    secondary:
      "bg-slate-100 text-slate-700 hover:bg-slate-200",

    outline:
      "border border-slate-300 bg-white text-slate-700 hover:bg-slate-100",

    gradient:
      "bg-gradient-to-r from-red-700 to-blue-800 text-white",
  };


  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-5 py-2.5 text-base",
    lg: "px-6 py-3 text-lg",
  };


  return (
    <button
      type={type}
      className={`
        rounded-xl
        font-medium
        transition-colors
        duration-200
        cursor-pointer

        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
};


export default Button;