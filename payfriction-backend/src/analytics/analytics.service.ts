import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class AnalyticsService {
  constructor(private prisma: PrismaService) {}

  // 1. Dashboard Summary
  async getDashboardSummary() {
    const revenueAtRisk = await this.prisma.transaction.aggregate({
      where: { status: 'FAILED' },
      _sum: { amount: true },
    });

    const failedCount = await this.prisma.transaction.count({
      where: { status: 'FAILED' },
    });

    return {
      revenueAtRisk: revenueAtRisk._sum.amount || 0,
      failedTransactions: failedCount,
    };
  }

  // 2. Gateway Performance
  async getGatewayPerformance() {
    const gateways = await this.prisma.paymentGateway.findMany({
      include: { attempts: true },
    });

    return gateways.map((gateway) => {
      const total = gateway.attempts.length;
      const successful = gateway.attempts.filter((a) => a.isSuccess).length;
      const failed = total - successful;
      const successRate = total > 0 ? ((successful / total) * 100).toFixed(1) : '0.0';

      return {
        gateway: gateway.name,
        totalAttempts: total,
        successful,
        failed,
        successRate: `${successRate}%`,
      };
    });
  }

  // 3. Error Breakdown
  async getErrorBreakdown() {
    const codes = await this.prisma.bankResponseCode.findMany({
      include: {
        _count: {
          select: { attempts: true },
        },
      },
    });

    return codes
      .filter((code) => code._count.attempts > 0)
      .map((code) => ({
        code: code.code,
        meaning: code.meaning,
        classification: code.classification,
        actionRequired: code.actionRequired,
        occurrences: code._count.attempts,
      }))
      .sort((a, b) => b.occurrences - a.occurrences);
  }

  // 4. Retry Metrics
  async getRetryMetrics() {
    const retries = await this.prisma.paymentAttempt.findMany({
      where: { attemptNumber: { gt: 1 } },
    });

    const totalRetries = retries.length;
    const successfulRetries = retries.filter((r) => r.isSuccess).length;
    const recoveryRate = totalRetries > 0 ? ((successfulRetries / totalRetries) * 100).toFixed(1) : '0.0';

    return {
      totalRetries,
      successfulRetries,
      recoveryRate: `${recoveryRate}%`,
    };
  }
}