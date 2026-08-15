import { Module } from '@nestjs/common';
import { OrdersModule } from './orders/orders.module';
import { PrismaModule } from './prisma/prisma.module'; // Import this
import { ConfigModule } from '@nestjs/config'; // Import this

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }), // Loads your .env file
    PrismaModule, 
    OrdersModule
  ],
})
export class AppModule {}