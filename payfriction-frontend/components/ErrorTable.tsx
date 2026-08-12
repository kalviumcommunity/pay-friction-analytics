"use client";

import { useQuery } from "@tanstack/react-query";
import axios from "axios";

interface ErrorData {
  code: string;
  meaning: string;
  classification: string;
  actionRequired: string;
  occurrences: number;
}

export default function ErrorTable() {
  const { data, isLoading, isError } = useQuery<ErrorData[]>({
    queryKey: ["error-breakdown"],
    queryFn: async () => {
      const response = await axios.get("http://localhost:3001/analytics/errors");
      return response.data;
    },
  });

  if (isLoading) return <div className="p-4 text-gray-500 bg-white rounded-xl border border-gray-200 min-h-64 flex items-center justify-center">Loading error data...</div>;
  if (isError) return <div className="p-4 text-red-500 bg-white rounded-xl border border-gray-200 min-h-64 flex items-center justify-center">Failed to load error data.</div>;

  // Helper function for badge colors
  const getBadgeStyle = (classification: string) => {
    if (classification === 'Success') return 'bg-green-100 text-green-700';
    if (classification === 'Permanent Failure') return 'bg-red-100 text-red-700';
    return 'bg-yellow-100 text-yellow-700'; // Temporary Friction
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mb-8">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Bank Response Codes</h3>
        <p className="text-sm text-gray-500">Breakdown of failure reasons and required actions</p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-gray-600">
          <thead className="bg-gray-50 text-gray-500 font-medium border-b border-gray-200">
            <tr>
              <th className="px-6 py-4">Code</th>
              <th className="px-6 py-4">Meaning</th>
              <th className="px-6 py-4">Classification</th>
              <th className="px-6 py-4">Action Required</th>
              <th className="px-6 py-4 text-right">Occurrences</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data?.map((error, index) => (
              <tr key={index} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 font-medium text-gray-900">{error.code}</td>
                <td className="px-6 py-4">{error.meaning}</td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getBadgeStyle(error.classification)}`}>
                    {error.classification}
                  </span>
                </td>
                <td className="px-6 py-4">{error.actionRequired}</td>
                <td className="px-6 py-4 text-right font-semibold text-gray-900">{error.occurrences}</td>
              </tr>
            ))}
            {data?.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                  No errors logged yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}