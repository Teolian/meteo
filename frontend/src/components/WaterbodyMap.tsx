import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import { Icon, LatLngExpression } from 'leaflet'
import { Waterbody } from '@/services/api'

// Fix for default markers in Vite/Webpack
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

delete (Icon.Default.prototype as any)._getIconUrl
Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
})

interface WaterbodyMapProps {
  waterbodies: Waterbody[]
  selectedWaterbody?: Waterbody
  onWaterbodySelect: (waterbody: Waterbody) => void
  className?: string
}

function MapController({ center }: { center: LatLngExpression }) {
  const map = useMap()

  useEffect(() => {
    map.setView(center, map.getZoom())
  }, [center, map])

  return null
}

export function WaterbodyMap({
  waterbodies,
  selectedWaterbody,
  onWaterbodySelect,
  className = '',
}: WaterbodyMapProps) {
  const center: LatLngExpression = selectedWaterbody
    ? [selectedWaterbody.lat, selectedWaterbody.lon]
    : [56.5, 38.0] // Central Russia

  return (
    <div className={className}>
      <MapContainer
        center={center}
        zoom={selectedWaterbody ? 10 : 6}
        className="h-full w-full rounded-xl"
        style={{ minHeight: '400px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {selectedWaterbody && <MapController center={center} />}

        {waterbodies.map((wb) => (
          <Marker
            key={wb.id}
            position={[wb.lat, wb.lon]}
            eventHandlers={{
              click: () => onWaterbodySelect(wb),
            }}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-semibold text-sm">{wb.name}</h3>
                <p className="text-xs text-muted-foreground">{wb.region}</p>
                <p className="text-xs text-muted-foreground capitalize">{wb.type}</p>
                <button
                  onClick={() => onWaterbodySelect(wb)}
                  className="mt-2 text-xs text-primary hover:underline"
                >
                  Выбрать →
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <p className="mt-2 text-xs text-muted-foreground">
        Карта: © OpenStreetMap contributors
      </p>
    </div>
  )
}
