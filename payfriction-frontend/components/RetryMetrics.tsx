"use client";

import { useQuery } from "@tanstack/react-query";
import axios from "axios";

// Define the shape of our retry data from the NestJS API
interface RetryData {
  totalRetries: number;
  successfulRetries: number;
  recoveryRate: string;
}

export default function RetryMetrics() {
  const { data, isLoading, isError } = useQuery<RetryData>({
    queryKey: ["retry-metrics"],
    queryFn: async () => {
      const response = await axios.get("http://localhost:3001/analytics/retries");
      return response.data;
    },
  });

  if (isLoading) return <div className="p-4 text-gray-500 bg-white rounded-xl border border-gray-200 mb-8">Loading retry metrics...</div>;
  if (isError) return <div className="p-4 text-red-500 bg-white rounded-xl border border-gray-200 mb-8">Failed to load retry metrics.</div>;

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Retry Recovery Rate</h3>
        <p className="text-sm text-gray-500">Transactions successfully recovered on the 2nd or 3rd attempt</p>
      </div>
      <div className="md:text-right">
        <p className="text-4xl font-semibold text-blue-600">{data?.recoveryRate}</p>
        <p className="text-sm font-medium text-gray-500 mt-1">
          {data?.successfulRetries} of {data?.totalRetries} retries succeeded
        </p>
      </div>
    </div>
  );
}