import { useEffect, useState } from "react";
import { Search, MapPin, BriefcaseBusiness, Phone, Mail } from "lucide-react";

import { getLawyers } from "../services/lawyerService";

const Lawyers = () => {
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


  const filteredLawyers = lawyers.filter((lawyer) =>
    lawyer.full_name
      .toLowerCase()
      .includes(search.toLowerCase())
  );


  return (
    <div className="h-full overflow-y-auto p-6 md:p-8">

      {/* Header */}

      <div className="mb-8">

        <h1 className="text-3xl font-bold text-slate-900">
          Lawyers Directory
        </h1>

        <p className="mt-2 text-slate-500">
          Find verified legal professionals for your legal needs.
        </p>

      </div>


      {/* Search */}

      <div className="mb-8">

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
            placeholder="Search lawyer by name..."
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
          gap-6
          sm:grid-cols-2
          xl:grid-cols-3
        ">

          {filteredLawyers.map((lawyer)=>(

            <div
              key={lawyer.id}
              className="
                rounded-2xl
                border
                border-slate-200
                bg-white
                p-6
                shadow-sm
                transition
                hover:-translate-y-1
                hover:shadow-lg
              "
            >


              {/* Profile */}

              <div className="flex items-center gap-4">

                {lawyer.profile_image ? (

                  <img
                    src={lawyer.profile_image}
                    alt={lawyer.full_name}
                    className="
                      h-16
                      w-16
                      rounded-full
                      object-cover
                    "
                  />

                ):(

                  <div className="
                    flex
                    h-16
                    w-16
                    items-center
                    justify-center
                    rounded-full
                    bg-[#C30A1C]
                    text-xl
                    font-bold
                    text-white
                  ">
                    {lawyer.full_name.charAt(0)}
                  </div>

                )}


                <div>

                  <h2 className="
                    font-semibold
                    text-slate-900
                  ">
                    {lawyer.full_name}
                  </h2>


                  <p className="
                    text-sm
                    text-slate-500
                  ">
                    {lawyer.specialization}
                  </p>

                </div>


              </div>


              {/* Info */}

              <div className="mt-5 space-y-3 text-sm text-slate-600">


                <div className="flex gap-2">

                  <BriefcaseBusiness size={17}/>

                  <span>
                    {lawyer.years_of_experience} years experience
                  </span>

                </div>



                <div className="flex gap-2">

                  <MapPin size={17}/>

                  <span>
                    {lawyer.city}
                  </span>

                </div>



                {lawyer.phone && (

                  <div className="flex gap-2">

                    <Phone size={17}/>

                    <span>
                      {lawyer.phone}
                    </span>

                  </div>

                )}



                {lawyer.email && (

                  <div className="flex gap-2">

                    <Mail size={17}/>

                    <span className="truncate">
                      {lawyer.email}
                    </span>

                  </div>

                )}

              </div>



              {/* Bio */}

              {lawyer.bio && (

                <p className="
                  mt-5
                  line-clamp-3
                  text-sm
                  leading-6
                  text-slate-500
                ">
                  {lawyer.bio}
                </p>

              )}


            </div>

          ))}


        </div>

      )}

    </div>
  );
};


export default Lawyers;