from discord.ext import commands
import discord
import codecs
import base64


class Ciphers(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="b64")
    async def b64(self,ctx,message,operation):
 
        if(operation == "e"):
            await ctx.send(str(base64.b64encode(str(message).encode("ascii"))).replace("'","").replace("b",""))
        elif(operation == "d"):
            await ctx.send(str(base64.b64decode(str(message).encode("ascii"))).replace("'","").replace("b",""))
        else:
            await ctx.send("Invalid Operation. e for encode, d for decode.")

    @commands.command(name="rot13")
    async def rot13(self,ctx,message,operation):
        if(operation == "e"):
            await ctx.send(str(codecs.encode(message, 'rot_13')))
        elif(operation == "d"):
            await ctx.send(str(codecs.decode(message,'rot_13')))
        else:
            await ctx.send("Invalid Operation. e for encode, d for decode.")

def setup(client):
    client.add_cog(Ciphers(client))
