import { Controller, Get } from '@nestjs/common';
import { AnalyticsService } from './analytics.service';

@Controller('analytics')
export class AnalyticsController {
  constructor(private readonly analyticsService: AnalyticsService) {}

  @Get('summary')
  async getSummary() {
    return this.analyticsService.getDashboardSummary();
  }

  @Get('gateways')
  async getGateways() {
    return this.analyticsService.getGatewayPerformance();
  }

  @Get('errors')
  async getErrors() {
    return this.analyticsService.getErrorBreakdown();
  }

  @Get('retries')
  async getRetries() {
    return this.analyticsService.getRetryMetrics();
  }
}