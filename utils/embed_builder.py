from discord import Embed


class EmbedBuilder:

    def build(em_dict):
        # Setting up title field
        em = Embed(title=em_dict.get('title', Embed.Empty), url=em_dict.get('url', Embed.Empty),
                   description=em_dict.get('description', Embed.Empty),color=0xde50d0)

        # Setting up author field
        if 'author' in em_dict:
            author_dict = em_dict.get('author')
            em.set_author(name=author_dict.get('name', Embed.Empty), url=author_dict.get('url', Embed.Empty),
                          icon_url=author_dict.get('icon_url', Embed.Empty))

        # Setting up thumbnail
        if 'thumbnail' in em_dict:
            em.set_thumbnail(url=em_dict.get('thumbnail'))

        # Setting up additional fields
        if 'extra' in em_dict:
            for field in em_dict.get('extra'):
                fields = em_dict.get('extra').get(field)
                em.add_field(name=field, value=fields.get('value', Embed.Empty),
                             inline=fields.get('inline', False))

        if 'image' in em_dict:
            em.set_image(url=em_dict.get('image', Embed.Empty))
        if 'footer' in em_dict:
            em.set_footer(text=em_dict.get('footer', Embed.Empty), icon_url=em_dict.get('icon_url', Embed.Empty))

        return em
