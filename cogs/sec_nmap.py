#!/usr/bin/python
import nmap
import logging
import discord
from discord.ext import commands

# Logging
logger = logging.getLogger('msecBot')
logger.debug(f"Logging enabled from: {__name__}")

class Sec_Nmap(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.allowed = False


    @commands.command()
    async def scan(self, ctx):
        """ Quick NMAP scan with T4 threads enabled by default.
        Takes target. Runs TCP scan. Provides IP in footer. """
        
        # Trusted member status roles
        trusted = ['Admin', 'IRL', 'Online Attendee']
        # Role names found from user who executed command
        role_names = [role.name for role in ctx.author.roles]
        
        # If user has a trusted role, toggle allow    
        for role in trusted:
            if role in role_names:
                self.allowed = True
                break

        if self.allowed:
            ports = []
            target = str(ctx.message.content)[6:]
            nm = nmap.PortScanner()
            results = nm.scan(target, arguments='-T4')
            
            # Some nmap parsing
            for IP in results['scan']: ip = IP
            for port in results['scan'][ip]['tcp']:
                ports.append(port)
            
            # Create embed message containing results
            xbed = discord.Embed(color = 0x00FF00)
            xbed.set_author(name = "NMAP Scan - v1.0",
            icon_url = "https://pentest-tools.com/blog/wp-content/uploads/2019/10/nmap-logo.png")
            xbed.set_footer(text = f'Target {target} ({ip})')
            
            # Some nmap parsing then stored in embed message
            for port in results['scan'][ip]['tcp']:
                p = results['scan'][ip]['tcp'][port]['state']
                xbed.add_field(name = 'Protocol', value = 'TCP')
                xbed.add_field(name = 'Port', value = str(port))
                xbed.add_field(name = 'State', value = results['scan'][ip]['tcp'][port]['state'])
            
            # Send embed message then toggle allow permission
            await ctx.send(embed = xbed)
            self.allowed = False

        # Permission issue prompt
        else:
            xbed = discord.Embed(color = 0xFF0000)
            xbed.set_author(name = "NMAP Scan - v1.0",
            icon_url = "https://pentest-tools.com/blog/wp-content/uploads/2019/10/nmap-logo.png")
            xbed.add_field(name = 'Permission Issue', value = 'To prevent possible abuse, you must \
                                 have the member role of "Online Attendee", "IRL" or "Admin".')
            await ctx.send(embed = xbed)

def setup(client):
    client.add_cog(Sec_Nmap(client))
