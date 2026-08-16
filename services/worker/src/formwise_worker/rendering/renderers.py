import fitz
from PIL import Image, ImageDraw, ImageFont


class _Base:
 def _eligible(self,field,assignment):
  m=field.get('renderMetadata',{});return m.get('privacyTier')=='safe' and assignment.get('status')=='approved'
 def _box(self,m):
  b=m.get('cellBounds') or m.get('boundingBox');return fitz.Rect(b['x'],b['y'],b['x']+b['width'],b['y']+b['height']) if b else None
class FillablePDFRenderer(_Base):
 name='fillable_pdf'
 def render(self,original,output,field_map,assignments):
  doc=fitz.open(original); warnings=[]
  for a in assignments:
   f=next((x for x in field_map if x.get('id')==a.get('fieldId')),None)
   if not f or not self._eligible(f,a):warnings.append(str(a.get('fieldId')));continue
   m=f['renderMetadata']; wid=m.get('widgetId'); xref=m.get('widgetXref'); page_number=m.get('pageNumber'); expected_type=m.get('widgetType')
   if not isinstance(xref,int) or not isinstance(page_number,int) or page_number<1 or page_number>len(doc): warnings.append(f"WIDGET_REFERENCE_INVALID:{a.get('fieldId')}");continue
   try: w=doc[page_number-1].load_widget(xref)
   except (RuntimeError, ValueError): w=None
   if not w or w.field_name!=wid or (expected_type is not None and str(w.field_type)!=expected_type): warnings.append(f"WIDGET_MISMATCH:{a.get('fieldId')}");continue
   w.field_value='Yes' if m.get('fieldType')=='checkbox' and str(a.get('value')).lower() in ('checked','true','yes') else str(a.get('value',''));w.update()
  doc.save(output);return len(doc),warnings
class StaticPDFRenderer(_Base):
 name='static_pdf'
 def render(self,original,output,field_map,assignments):
  doc=fitz.open(original);warnings=[]
  for a in assignments:
   f=next((x for x in field_map if x.get('id')==a.get('fieldId')),None)
   if not f or not self._eligible(f,a):warnings.append(str(a.get('fieldId')));continue
   m=f['renderMetadata'];r=self._box(m);p=int(m.get('pageNumber',0))-1
   if r is None or p<0 or p>=len(doc):warnings.append(str(a.get('fieldId')));continue
   doc[p].insert_textbox(r,'✓' if m.get('fieldType')=='checkbox' and str(a.get('value')).lower() in ('checked','true','yes') else str(a.get('value','')),fontsize=10,align={'left':0,'center':1,'right':2}.get(m.get('textAlignment'),0),fontname='helv')
  doc.save(output);return len(doc),warnings
class ImageRenderer(_Base):
 name='image'
 def render(self,original,output,field_map,assignments):
  im=Image.open(original).convert('RGB');d=ImageDraw.Draw(im);warnings=[]
  for a in assignments:
   f=next((x for x in field_map if x.get('id')==a.get('fieldId')),None)
   if not f or not self._eligible(f,a):warnings.append(str(a.get('fieldId')));continue
   b=(f['renderMetadata'].get('cellBounds') or f['renderMetadata'].get('boundingBox'))
   if not b:warnings.append(str(a.get('fieldId')));continue
   d.text((b['x'],b['y']),'✓' if f['renderMetadata'].get('fieldType')=='checkbox' else str(a.get('value','')),fill='black',font=ImageFont.load_default())
  im.save(output);return 1,warnings
