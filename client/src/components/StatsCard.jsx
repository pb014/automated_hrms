const StatsCard = ({ title, value, icon: Icon, color = "indigo" }) => {
  const colorMap = {
    indigo: "bg-indigo-50 text-indigo-600",
    green: "bg-green-50 text-green-600",
    amber: "bg-amber-50 text-amber-600",
    red: "bg-red-50 text-red-600",
    blue: "bg-blue-50 text-blue-600",
  };
  return (
    <div className='bg-white rounded-xl border border-gray-200 p-5'>
      <div className='flex items-center justify-between'>
        <div>
          <p className='text-sm text-gray-500'>{title}</p>
          <p className='text-2xl font-bold text-gray-800 mt-1'>{value}</p>
        </div>
        {Icon && (
          <div
            className={`p-3 rounded-lg ${colorMap[color] || colorMap.indigo}`}>
            <Icon className='w-6 h-6' />
          </div>
        )}
      </div>
    </div>
  );
};

export default StatsCard;
