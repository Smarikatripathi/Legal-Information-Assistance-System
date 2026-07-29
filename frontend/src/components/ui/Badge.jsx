const Badge = ({
  children,
  variant = "default",
  size = "md",
  className = "",
  ...props
}) => {
  const variants = {
    default: "bg-slate-100 text-slate-700",
    primary: "bg-[#084FF4]/10 text-[#084FF4]",
    success: "bg-green-100 text-green-700",
    warning: "bg-amber-100 text-amber-700",
    danger: "bg-red-100 text-red-700",
    info: "bg-sky-100 text-sky-700",
  };

  const sizes = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-sm",
    lg: "px-4 py-1.5 text-base",
  };

  return (
    <span
      className={`
        inline-flex
        items-center
        justify-center
        rounded-full
        font-medium
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {children}
    </span>
  );
};

export default Badge;
