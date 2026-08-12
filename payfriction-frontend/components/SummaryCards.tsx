"use client";

import { useQuery } from "@tanstack/react-query";
import axios from "axios";

// Define the shape of our API response
interface SummaryData {
  revenueAtRisk: string | number;
  failedTransactions: number;
}

export default function SummaryCards() {
  const { data, isLoading, isError } = useQuery<SummaryData>({
    queryKey: ["dashboard-summary"],
    queryFn: async () => {
      const response = await axios.get("http://localhost:3001/analytics/summary");
      return response.data;
    },
  });

  if (isLoading) return <div className="p-4 text-gray-500">Loading metrics...</div>;
  if (isError) return <div className="p-4 text-red-500">Failed to load metrics.</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      {/* Revenue at Risk Card */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
          Revenue at Risk
        </h3>
        <p className="mt-2 text-4xl font-semibold text-red-600">
          ${Number(data?.revenueAtRisk).toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </p>
      </div>

      {/* Failed Transactions Card */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
          Failed Transactions
        </h3>
        <p className="mt-2 text-4xl font-semibold text-gray-900">
          {data?.failedTransactions.toLocaleString()}
        </p>
      </div>
    </div>
  );
}