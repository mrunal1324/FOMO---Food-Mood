import { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Snackbar,
  Alert,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import SentimentVerySatisfiedIcon from '@mui/icons-material/SentimentVerySatisfied';
import RestaurantIcon from '@mui/icons-material/Restaurant';

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#FF6B6B',
    },
    secondary: {
      main: '#4ECDC4',
    },
    background: {
      default: '#F7F7F7',
    },
  },
  typography: {
    fontFamily: '"Poppins", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// Styled components
const StyledCard = styled(Card)(({ theme }) => ({
  marginTop: theme.spacing(4),
  borderRadius: 16,
  boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
  transition: 'transform 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateY(-4px)',
  },
  [theme.breakpoints.down('sm')]: {
    marginTop: theme.spacing(2),
    borderRadius: 12,
  },
}));

const MoodInput = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 12,
    backgroundColor: 'white',
  },
  [theme.breakpoints.down('sm')]: {
    '& .MuiOutlinedInput-root': {
      borderRadius: 8,
    },
  },
}));

const SubmitButton = styled(Button)(({ theme }) => ({
  borderRadius: 12,
  padding: '12px 24px',
  textTransform: 'none',
  fontWeight: 600,
  [theme.breakpoints.down('sm')]: {
    borderRadius: 8,
    padding: '10px 20px',
  },
}));

interface FoodRecommendation {
  name: string;
  confidence: number;
}

interface StoredRecommendation {
  mood: string;
  recommendations: string[];
  selectedFood: string;
  temperature: number;
  location: string;
  timestamp: string;
}

function App() {
  const [mood, setMood] = useState('');
  const [recommendations, setRecommendations] = useState<FoodRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedFood, setSelectedFood] = useState<string>('');
  const [showSelection, setShowSelection] = useState(false);
  const [storedRecommendations, setStoredRecommendations] = useState<StoredRecommendation[]>([]);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [location, setLocation] = useState<string>('');
  const [temperature, setTemperature] = useState<number | null>(null);

  useEffect(() => {
    // Load stored recommendations from localStorage
    const stored = localStorage.getItem('foodRecommendations');
    if (stored) {
      setStoredRecommendations(JSON.parse(stored));
    }

    // Get user's location and temperature
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          try {
            // Get location name from coordinates
            const locationResponse = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
            );
            const locationData = await locationResponse.json();
            setLocation(locationData.display_name.split(',')[0]);

            // Get temperature from OpenWeatherMap API
            const weatherResponse = await fetch(
              `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=YOUR_API_KEY&units=metric`
            );
            const weatherData = await weatherResponse.json();
            setTemperature(weatherData.main.temp);
          } catch (error) {
            console.error('Error fetching location data:', error);
          }
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setRecommendations([]);
    setSelectedFood('');
    setShowSelection(false);

    // Check if we have a stored recommendation for this mood
    const storedRec = storedRecommendations.find(
      rec => rec.mood.toLowerCase() === mood.toLowerCase()
    );

    if (storedRec) {
      setRecommendations(storedRec.recommendations.map(rec => ({
        name: rec,
        confidence: 1.0
      })));
      setSelectedFood(storedRec.selectedFood);
      setShowSelection(true);
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: mood,
          temperature: temperature,
          location: location
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get recommendations');
      }

      const data = await response.json();
      const newRecommendations = data.recommendations.map((rec: string) => ({
        name: rec,
        confidence: 1.0
      }));
      setRecommendations(newRecommendations);
      setShowSelection(true);
    } catch (err) {
      setError('Failed to get food recommendations. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFoodSelection = async (food: string) => {
    setSelectedFood(food);
    setShowConfirmation(true);

    // Store the recommendation
    const newStoredRec: StoredRecommendation = {
      mood,
      recommendations: recommendations.map(rec => rec.name),
      selectedFood: food,
      temperature: temperature || 0,
      location: location || 'Unknown',
      timestamp: new Date().toISOString()
    };

    const updatedStored = [...storedRecommendations, newStoredRec];
    setStoredRecommendations(updatedStored);
    localStorage.setItem('foodRecommendations', JSON.stringify(updatedStored));

    // Save to user_data.json through backend
    try {
      await fetch('http://localhost:5000/api/save-user-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newStoredRec),
      });
    } catch (error) {
      console.error('Error saving user data:', error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          bgcolor: 'background.default',
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          overflow: 'auto',
        }}
      >
        <Container maxWidth="md" sx={{ width: '100%', py: 4 }}>
          <Box sx={{ 
            textAlign: 'center',
            px: { xs: 2, sm: 0 },
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Typography
              variant="h2"
              component="h1"
              gutterBottom
              sx={{
                fontWeight: 700,
                color: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 2,
                fontSize: { xs: '2.5rem', sm: '3.75rem' },
              }}
            >
              <SentimentVerySatisfiedIcon sx={{ fontSize: { xs: 36, sm: 48 } }} />
              Mood Food
            </Typography>
            
            <Typography 
              variant="h5" 
              color="text.secondary" 
              sx={{ 
                mb: 4,
                fontSize: { xs: '1.25rem', sm: '1.5rem' },
                px: { xs: 2, sm: 0 },
                maxWidth: '600px',
              }}
            >
              Tell us how you're feeling, and we'll recommend the perfect food for your mood!
            </Typography>

            <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '600px' }}>
              <Grid container spacing={2} justifyContent="center">
                <Grid item xs={12} sm={8}>
                  <MoodInput
                    fullWidth
                    label="How are you feeling today?"
                    variant="outlined"
                    value={mood}
                    onChange={(e) => setMood(e.target.value)}
                    placeholder="e.g., happy, tired, stressed..."
                    required
                    size="medium"
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <SubmitButton
                    fullWidth
                    variant="contained"
                    type="submit"
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <RestaurantIcon />}
                    sx={{ height: { xs: '48px', sm: '56px' } }}
                  >
                    Get Recommendations
                  </SubmitButton>
                </Grid>
              </Grid>
            </form>

            {error && (
              <Typography 
                color="error" 
                sx={{ 
                  mt: 2,
                  px: { xs: 2, sm: 0 }
                }}
              >
                {error}
              </Typography>
            )}

            {recommendations.length > 0 && (
              <StyledCard sx={{ width: '100%', maxWidth: '600px', mt: 4 }}>
                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                  <Typography 
                    variant="h5" 
                    gutterBottom 
                    sx={{ 
                      fontWeight: 600,
                      fontSize: { xs: '1.25rem', sm: '1.5rem' }
                    }}
                  >
                    Recommended Foods for your {mood} mood:
                    {temperature && location && (
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Current temperature in {location}: {temperature}°C
                      </Typography>
                    )}
                  </Typography>
                  
                  {showSelection ? (
                    <FormControl component="fieldset" sx={{ width: '100%', mt: 2 }}>
                      <RadioGroup
                        value={selectedFood}
                        onChange={(e) => handleFoodSelection(e.target.value)}
                        sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
                      >
                        {recommendations.map((rec, index) => (
                          <Box
                            key={index}
                            sx={{
                              p: { xs: 1.5, sm: 2 },
                              bgcolor: 'background.paper',
                              borderRadius: 2,
                              display: 'flex',
                              alignItems: 'center',
                              gap: 2,
                              boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                              border: selectedFood === rec.name ? '2px solid #FF6B6B' : 'none',
                              transition: 'all 0.2s ease-in-out',
                              '&:hover': {
                                border: '2px solid #FF6B6B',
                              },
                            }}
                          >
                            <FormControlLabel
                              value={rec.name}
                              control={<Radio color="primary" />}
                              label={
                                <Box sx={{ flex: 1, textAlign: 'left' }}>
                                  <Typography 
                                    variant="h6" 
                                    sx={{ 
                                      fontSize: { xs: '1rem', sm: '1.25rem' }
                                    }}
                                  >
                                    {rec.name}
                                  </Typography>
                                  <Typography 
                                    variant="body2" 
                                    color="text.secondary"
                                    sx={{ 
                                      fontSize: { xs: '0.875rem', sm: '1rem' }
                                    }}
                                  >
                                    Confidence: {(rec.confidence * 100).toFixed(0)}%
                                  </Typography>
                                </Box>
                              }
                              sx={{ width: '100%', m: 0 }}
                            />
                          </Box>
                        ))}
                      </RadioGroup>
                    </FormControl>
                  ) : (
                    <Grid container spacing={2}>
                      {recommendations.map((rec, index) => (
                        <Grid item xs={12} key={index}>
                          <Box
                            sx={{
                              p: { xs: 1.5, sm: 2 },
                              bgcolor: 'background.paper',
                              borderRadius: 2,
                              display: 'flex',
                              alignItems: 'center',
                              gap: 2,
                              boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                            }}
                          >
                            <RestaurantIcon 
                              color="primary" 
                              sx={{ fontSize: { xs: 24, sm: 32 } }}
                            />
                            <Box sx={{ flex: 1 }}>
                              <Typography 
                                variant="h6" 
                                sx={{ 
                                  fontSize: { xs: '1rem', sm: '1.25rem' }
                                }}
                              >
                                {rec.name}
                              </Typography>
                              <Typography 
                                variant="body2" 
                                color="text.secondary"
                                sx={{ 
                                  fontSize: { xs: '0.875rem', sm: '1rem' }
                                }}
                              >
                                Confidence: {(rec.confidence * 100).toFixed(0)}%
                              </Typography>
                            </Box>
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  )}
                </CardContent>
              </StyledCard>
            )}
          </Box>
        </Container>
      </Box>

      <Snackbar
        open={showConfirmation}
        autoHideDuration={3000}
        onClose={() => setShowConfirmation(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setShowConfirmation(false)} 
          severity="success" 
          sx={{ width: '100%' }}
        >
          Your selection has been saved! We'll remember this for next time you're feeling {mood}.
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;
