import { useEffect, useState } from "react";
import { Search, MapPin, BriefcaseBusiness, Mail, User } from "lucide-react";
import { useNavigate, useOutletContext } from "react-router-dom";

import { getLawyers } from "../services/lawyerService";
import Breadcrumb from "../components/ui/Breadcrumb";

const Lawyers = () => {
  const navigate = useNavigate();
  const { filters = { location: "", practiceAreas: [], experience: "All" }, setFilters = () => {}, availableLocations = [], setAvailableLocations = () => {} } = useOutletContext();
  const [lawyers, setLawyers] = useState([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchLawyers();
  }, []);

  const fetchLawyers = async () => {
    try {
      setLoading(true);

      const data = await getLawyers();

      setLawyers(data);
    } catch (error) {
      console.error("Failed to load lawyers:", error);
    } finally {
      setLoading(false);
    }
  };

  // Update available locations in parent context when lawyers load
  useEffect(() => {
    if (setAvailableLocations && lawyers.length > 0) {
      const locations = [...new Set(lawyers.map((lawyer) => lawyer.city))];
      setAvailableLocations(locations);
    }
  }, [lawyers, setAvailableLocations]);

  // Filter lawyers based on search and sidebar filters
  const filteredLawyers = lawyers.filter((lawyer) => {
    // Search filter
    const matchesSearch =
      lawyer.full_name.toLowerCase().includes(search.toLowerCase()) ||
      lawyer.specialization.toLowerCase().includes(search.toLowerCase()) ||
      lawyer.city.toLowerCase().includes(search.toLowerCase());

    // Location filter
    const matchesLocation = filters.location === "" || lawyer.city === filters.location;

    // Practice area filter (check if lawyer's specialization matches any selected practice area)
    const matchesPracticeArea =
      filters.practiceAreas.length === 0 ||
      filters.practiceAreas.some((area) =>
        lawyer.specialization.toLowerCase().includes(area.toLowerCase())
      );

    // Experience filter
    let matchesExperience = true;
    if (filters.experience === "0-2 years") {
      matchesExperience = lawyer.years_of_experience <= 2;
    } else if (filters.experience === "3-5 years") {
      matchesExperience = lawyer.years_of_experience >= 3 && lawyer.years_of_experience <= 5;
    } else if (filters.experience === "5+ years") {
      matchesExperience = lawyer.years_of_experience > 5;
    }

    return matchesSearch && matchesLocation && matchesPracticeArea && matchesExperience;
  });


  return (
    <div className="flex h-full flex-col w-full max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-4 md:py-6 overflow-y-auto">

      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Lawyers Directory" },
        ]}
      />

      {/* Header */}

      <div className="mb-6">

        <h1 className="text-2xl font-bold text-slate-900">
          Lawyers Directory
        </h1>

        <p className="mt-1 text-sm text-slate-500">
          Find verified legal professionals for your legal needs.
        </p>

      </div>


      {/* Search */}

      <div className="mb-6">

        <div className="
          flex
          items-center
          gap-3
          rounded-xl
          border
          border-slate-200
          bg-white
          px-4
          py-3
          shadow-sm
        ">

          <Search
            size={20}
            className="text-slate-400"
          />

          <input
            value={search}
            onChange={(e)=>setSearch(e.target.value)}
            placeholder="Search by name, specialization, or location..."
            className="
              w-full
              outline-none
              text-sm
              text-slate-700
            "
          />

        </div>

      </div>



      {/* Loading */}

      {loading && (

        <div className="flex justify-center py-20 text-slate-500">
          Loading lawyers...
        </div>

      )}



      {/* Empty */}

      {!loading && filteredLawyers.length === 0 && (

        <div className="
          rounded-2xl
          bg-white
          p-10
          text-center
          shadow-sm
        ">

          <p className="text-slate-500">
            No lawyers found.
          </p>

        </div>

      )}



      {/* Lawyers Grid */}

      {!loading && filteredLawyers.length > 0 && (

        <div className="
          grid
          gap-4
          grid-cols-1
          md:grid-cols-2
          xl:grid-cols-3
        ">

          {filteredLawyers.map((lawyer)=>(

            <div
              key={lawyer.id}
              className="
                flex
                flex-col
                rounded-xl
                border
                border-slate-200
                bg-white
                p-4
                shadow-sm
                transition-all
                duration-300
                hover:-translate-y-1
                hover:shadow-xl
                hover:border-slate-300
              "
            >


              {/* Profile */}

              <div className="flex items-center gap-3 shrink-0">

                {lawyer.profile_image ? (

                  <img
                    src={lawyer.profile_image}
                    alt={lawyer.full_name}
                    className="
                      h-12
                      w-12
                      shrink-0
                      rounded-full
                      object-cover
                      shadow-md
                    "
                  />

                ):(

                  <div className="
                    flex
                    h-12
                    w-12
                    shrink-0
                    items-center
                    justify-center
                    rounded-full
                    bg-accent
                    text-lg
                    font-bold
                    text-white
                    shadow-md
                  ">
                    {lawyer.full_name.charAt(0)}
                  </div>

                )}


                <div className="min-w-0">

                  <h2 className="
                    font-semibold
                    text-sm
                    text-slate-900
                    truncate
                  ">
                    {lawyer.full_name}
                  </h2>


                  <p className="
                    text-xs
                    text-slate-500
                    truncate
                  ">
                    {lawyer.specialization}
                  </p>

                </div>


              </div>


              {/* Info */}

              <div className="mt-4 space-y-2 text-xs text-slate-600 shrink-0">


                <div className="flex gap-2">

                  <BriefcaseBusiness size={14} className="shrink-0"/>

                  <span>
                    {lawyer.years_of_experience} years experience
                  </span>

                </div>



                <div className="flex gap-2">

                  <MapPin size={14} className="shrink-0"/>

                  <span>
                    {lawyer.city}
                  </span>

                </div>



                {lawyer.email && (

                  <div className="flex gap-2">

                    <Mail size={14} className="shrink-0"/>

                    <a
                      href={`https://mail.google.com/mail/?view=cm&fs=1&to=${lawyer.email}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="truncate cursor-pointer hover:text-[#084FF4] hover:underline transition-colors"
                    >
                      {lawyer.email}
                    </a>

                  </div>

                )}

              </div>



              {/* Bio */}

              {lawyer.bio && (

                <p className="
                  mt-4
                  line-clamp-2
                  text-xs
                  leading-5
                  text-slate-500
                  flex-1
                ">
                  {lawyer.bio}
                </p>

              )}


              {/* Action Buttons */}
              <div className="mt-4 flex gap-2 shrink-0">
                {lawyer.email && (
                  <a
                    href={`https://mail.google.com/mail/?view=cm&fs=1&to=${lawyer.email}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="
                      flex-1
                      flex
                      items-center
                      justify-center
                      gap-2
                      rounded-lg
                      border
                      border-slate-200
                      bg-white
                      px-3
                      py-2
                      text-xs
                      font-medium
                      text-slate-700
                      cursor-pointer
                      transition-all
                      duration-200
                      hover:border-[#084FF4]
                      hover:bg-[#084FF4]
                      hover:text-white
                      focus:outline-none
                      focus:ring-2
                      focus:ring-[#084FF4]
                      focus:ring-offset-2
                    "
                  >
                    <Mail size={14} />
                    Email
                  </a>
                )}

                <button
                  onClick={() => navigate(`/dashboard/lawyers/${lawyer.id}`)}
                  className="
                    flex-1
                    flex
                    items-center
                    justify-center
                    gap-2
                    rounded-lg
                    border
                    border-slate-200
                    bg-white
                    px-3
                    py-2
                    text-xs
                    font-medium
                    text-slate-700
                    transition-all
                    duration-200
                    hover:border-accent
                    hover:bg-accent
                    hover:text-white
                    focus:outline-none
                    focus:ring-2
                    focus:ring-accent
                    focus:ring-offset-2
                  "
                >
                  <User size={14} />
                  View Profile
                </button>
              </div>


            </div>

          ))}


        </div>

      )}

    </div>
  );
};

export default Lawyers;