import { Controller, Get } from '@nestjs/common';
import { OrdersService } from './orders.service';

@Controller('api/orders')
export class OrdersController {
  constructor(private readonly ordersService: OrdersService) {}

  @Get()
  getAllOrders() {
    return this.ordersService.getAllOrders();
  }

  @Get('metrics')
  getMetrics() {
    return this.ordersService.getDashboardMetrics();
  }
}