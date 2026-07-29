const Avatar = ({
  src,
  alt,
  name,
  size = "md",
  className = "",
  ...props
}) => {
  const sizes = {
    xs: "h-6 w-6 text-xs",
    sm: "h-8 w-8 text-sm",
    md: "h-10 w-10 text-base",
    lg: "h-12 w-12 text-lg",
    xl: "h-16 w-16 text-xl",
    "2xl": "h-20 w-20 text-2xl",
  };

  const getInitials = (name) => {
    if (!name) return "";
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const backgroundColor = name
    ? `hsl(${name.length * 137.5 % 360}, 70%, 50%)`
    : "#cbd5e1";

  if (src) {
    return (
      <img
        src={src}
        alt={alt || name}
        className={`
          rounded-full
          object-cover
          ${sizes[size]}
          ${className}
        `}
        {...props}
      />
    );
  }

  return (
    <div
      className={`
        flex
        items-center
        justify-center
        rounded-full
        bg-gradient-to-br
        from-[#C30A1C]
        to-[#8a0614]
        text-white
        font-semibold
        shadow-md
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {getInitials(name) || "?"}
    </div>
  );
};

export default Avatar;
