import { Global, Module } from '@nestjs/common';
import { PrismaService } from './prisma.service';

@Global() // <-- Makes Prisma available app-wide
@Module({
  providers: [PrismaService],
  exports: [PrismaService], // <-- Allows other modules to use it
})
export class PrismaModule {}